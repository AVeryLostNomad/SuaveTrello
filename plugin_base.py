# Decorator for triggers
# A trigger is an event that we can watch.
# We expect it to return True if the event has happened and False if not.
# If it has 'required_arg_types', then the trigger will request those arguments in the console
# and will be passed them at runtime.
class Trigger():
	def __init__(self, name, description, required_arg_types=[], generated_arg_types=[]):
		self.trigger = True
		self.tname = name
		self.tdesc = description
		self.treqs = required_arg_types
		self.tgen = generated_arg_types

	def __call__(self, f):
		f.trigger = self.trigger
		f.tname = self.tname
		f.tdesc = self.tdesc
		f.treqs = self.treqs
		f.tgen = self.tgen
		return f

# Decorator for actions
# An action is a method that we should be able to call to perform some arbitrary thing.
# they can be put into the requested parameters of a trigger to generate something, but this
# will cause them to run every check of the trigger -- which may or may not be ideal.
# An Action can also have required arguments, which would be requested in the console and
# passed at runtime
# Actions will most typically be called as a result of an event trigger returning True. IE
# Person arriving home code triggers -> Turn on lights action
class Action():
	def __init__(self, name, description, required_arg_types=[], generated_arg_types=[]):
		self.action = True
		self.aname = name
		self.adesc = description
		self.areqs = required_arg_types
		self.agen = generated_arg_types

	def __call__(self, f):
		f.action = self.action
		f.aname = self.aname
		f.adesc = self.adesc
		f.areqs = self.areqs
		f.agen = self.agen
		return f

# Decorator for any actions that must be run before Suave is opened. This can be where background services
# are started, models are loaded, or files are created.
# They are optional, but will be called before any flow when Suave first launches.
class Prelaunch():
    def __init__(self):
        self.prelaunch = True

    def __call__(self, f):
        f.prelaunch = self.prelaunch
        return f
