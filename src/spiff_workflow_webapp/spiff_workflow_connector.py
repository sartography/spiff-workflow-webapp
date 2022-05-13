"""Spiff Workflow Connector."""
import argparse
import json
import sys
import traceback

from jinja2 import Template
from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.specs.events.event_types import CatchingEvent
from SpiffWorkflow.bpmn.specs.events.event_types import ThrowingEvent
from SpiffWorkflow.bpmn.specs.ManualTask import ManualTask
from SpiffWorkflow.bpmn.specs.ScriptTask import ScriptTask
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter
from SpiffWorkflow.camunda.specs.UserTask import EnumFormField
from SpiffWorkflow.camunda.specs.UserTask import UserTask
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter
from SpiffWorkflow.task import Task

# from custom_script_engine import CustomScriptEngine

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(
    [UserTaskConverter, BusinessRuleTaskConverter]
)
serializer = BpmnWorkflowSerializer(wf_spec_converter)


class Parser(BpmnDmnParser):
    """Parser."""

    OVERRIDE_PARSER_CLASSES = BpmnDmnParser.OVERRIDE_PARSER_CLASSES
    OVERRIDE_PARSER_CLASSES.update(CamundaParser.OVERRIDE_PARSER_CLASSES)


def parse(process, bpmn_files, dmn_files):
    """Parse."""
    parser = Parser()
    parser.add_bpmn_files(bpmn_files)
    if dmn_files:
        parser.add_dmn_files(dmn_files)
    return BpmnWorkflow(parser.get_spec(process))


def select_option(prompt, options):
    """Select_option."""
    option = input(prompt)
    while option not in options:
        print("Invalid selection")
        option = input(prompt)
    return option


def display_task(task):
    """Display_task."""
    print(f"\n{task.task_spec.description}")
    if task.task_spec.documentation is not None:
        template = Template(task.task_spec.documentation)
        print(template.render(task.data))


def format_task(task, include_state=True):
    """Format_task."""
    if hasattr(task.task_spec, "lane") and task.task_spec.lane is not None:
        lane = f"[{task.task_spec.lane}]"
    else:
        lane = ""
    state = f"[{task.get_state_name()}]" if include_state else ""
    return f"{lane} {task.task_spec.description} ({task.task_spec.name}) {state}"


def complete_user_task(task, answer=None):
    """Complete_user_task."""
    display_task(task)
    required_user_input_fields = {}
    if task.data is None:
        task.data = {}

    for field in task.task_spec.form.fields:
        if isinstance(field, EnumFormField):
            option_map = {opt.name: opt.id for opt in field.options}
            options = "(" + ", ".join(option_map) + ")"
            if answer is None:
                required_user_input_fields[field.label] = options
            else:
                response = option_map[answer]
        else:
            if answer is None:
                required_user_input_fields[field.label] = "(1..)"
            else:
                if field.type == "long":
                    response = int(answer)
        task.update_data_var(field.id, response)
    return required_user_input_fields


def complete_manual_task(task):
    """Complete_manual_task."""
    display_task(task)
    input("Press any key to mark task complete")


def print_state(workflow):
    """Print_state."""
    task = workflow.last_task
    print("\nLast Task")
    print(format_task(task))
    print(json.dumps(task.data, indent=2, separators=[", ", ": "]))

    display_types = (UserTask, ManualTask, ScriptTask, ThrowingEvent, CatchingEvent)
    all_tasks = [
        task
        for task in workflow.get_tasks()
        if isinstance(task.task_spec, display_types)
    ]
    upcoming_tasks = [
        task for task in all_tasks if task.state in [Task.READY, Task.WAITING]
    ]

    print("\nUpcoming Tasks")
    for _idx, task in enumerate(upcoming_tasks):
        print(format_task(task))

    if input("\nShow all tasks? ").lower() == "y":
        for _idx, task in enumerate(all_tasks):
            print(format_task(task))


def run(workflow, task_identifier=None, answer=None):
    """Run."""
    step = True
    workflow.do_engine_steps()

    while not workflow.is_completed():

        ready_tasks = workflow.get_ready_user_tasks()
        options = {}
        formatted_options = {}

        for idx, task in enumerate(ready_tasks):
            option = format_task(task, False)
            options[str(idx + 1)] = task
            formatted_options[str(idx + 1)] = option

        if task_identifier is None:
            return formatted_options

        # selected = None
        # while selected not in options and selected not in ["", "D", "d", "exit"]:
        #     selected = input(
        #         "Select task to complete, enter to wait, or D to dump the workflow state: "
        #     )

        # if selected.lower() == "d":
        #     filename = input("Enter filename: ")
        #     state = serializer.serialize_json(workflow)
        #     with open(filename, "w") as dump:
        #         dump.write(state)
        # elif selected == "exit":
        #     exit()
        next_task = options[task_identifier]
        if isinstance(next_task.task_spec, UserTask):
            if answer is None:
                return complete_user_task(next_task)
            else:
                complete_user_task(next_task, answer)
                next_task.complete()
        elif isinstance(next_task.task_spec, ManualTask):
            complete_manual_task(next_task)
            next_task.complete()
        else:
            next_task.complete()

        workflow.refresh_waiting_tasks()
        workflow.do_engine_steps()
        if step:
            print_state(workflow)

    print("\nWorkflow Data")
    print(json.dumps(workflow.data, indent=2, separators=[", ", ": "]))


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Simple BPMN runner")
    parser.add_argument(
        "-p", "--process", dest="process", help="The top-level BPMN Process ID"
    )
    parser.add_argument(
        "-b", "--bpmn", dest="bpmn", nargs="+", help="BPMN files to load"
    )
    parser.add_argument("-d", "--dmn", dest="dmn", nargs="*", help="DMN files to load")
    parser.add_argument(
        "-r",
        "--restore",
        dest="restore",
        metavar="FILE",
        help="Restore state from %(metavar)s",
    )
    parser.add_argument(
        "-s",
        "--step",
        dest="step",
        action="store_true",
        help="Display state after each step",
    )
    args = parser.parse_args()

    try:
        if args.restore is not None:
            with open(args.restore) as state:
                wf = serializer.deserialize_json(state.read())
        else:
            wf = parse(args.process, args.bpmn, args.dmn)
        run(wf, args.step)
    except Exception:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
