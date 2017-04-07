import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

Builder.load_file('./problem4.kv')

# Create the two screen
class menuScreen(Screen):
	def stop(self):
		exit()

class settingsScreen(Screen):
	pass

sm = ScreenManager(transition=NoTransition())
sm.add_widget(menuScreen(name='menu'))
sm.add_widget(settingsScreen(name='settings'))

class problem4App(App):
	def build(self):
		return sm


p4 = problem4App()
p4.run()






