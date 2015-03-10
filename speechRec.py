from dragonfly.all import Grammar, CompoundRule
import sys
from dragonfly.actions.action_function import Function


# Voice command rule combining spoken form and recognition processing.
class ExampleRule(CompoundRule):
    spec = "do something computer"   # Spoken form of command.

    def _process_recognition(self, node, extras):   # Callback when command is spoken.
        print("Voice command spoken.")

# Create a grammar which contains and loads the command rule.
grammar = Grammar("example grammar")                # Create a grammar to contain the command rule.
grammar.add_rule(ExampleRule())                     # Add the command rule to the grammar.
grammar.load()                                      # Load the grammar.


def myFunt(action):
    print("Action:", action)



def hey():
    #pythoncom.PumpWaitingMessages()
    sys.sleep(.1)
    action = Function(myFunt)
    action.execute({"action": "hey there!"})