import pygame
import glfw

class Key(object):
	def __init__(self, pygameKey, glfwKey):
		self.Pygame = pygameKey
		self.Glfw = glfwKey

class KeyMod(object):
	def __init__(self, pygameMod, glfwMod):
		self.Pygame = pygameMod
		self.Glfw = glfwMod

class MouseButton(object):
	def __init__(self, pygameButton, glfwButton):
		self.Pygame = pygameButton
		self.Glfw = glfwButton

class MouseButtons:
	Left = 				MouseButton(1, 				glfw.MOUSE_BUTTON_LEFT)
	Middle = 			MouseButton(2, 				glfw.MOUSE_BUTTON_MIDDLE)
	Right = 			MouseButton(3, 				glfw.MOUSE_BUTTON_RIGHT)

class KeyMods:
	ModShift = 			KeyMod(pygame.KMOD_SHIFT, 	glfw.MOD_SHIFT)
	ModControl = 		KeyMod(pygame.KMOD_CTRL, 	glfw.MOD_CONTROL)
	ModAlt = 			KeyMod(pygame.KMOD_ALT, 	glfw.MOD_ALT)
	ModSuper = 			KeyMod(-1, 					glfw.MOD_SUPER)
	ModCapsLock = 		KeyMod(pygame.KMOD_CAPS, 	glfw.MOD_CAPS_LOCK)
	ModNumLock = 		KeyMod(pygame.KMOD_NUM, 	glfw.MOD_NUM_LOCK)

class Keys:
	KeyInvalid = 		Key(-1, 					glfw.KEY_UNKNOWN)
	#special
	KeySpace = 			Key(pygame.K_SPACE, 		glfw.KEY_SPACE)
	KeyApostrophe = 	Key(pygame.K_QUOTE, 	glfw.KEY_APOSTROPHE)
	KeyComma = 			Key(pygame.K_COMMA, 		glfw.KEY_COMMA)
	KeyMinus = 			Key(pygame.K_MINUS, 		glfw.KEY_MINUS)
	KeyPeriod = 		Key(pygame.K_PERIOD, 		glfw.KEY_PERIOD)
	KeySlash = 			Key(pygame.K_SLASH, 		glfw.KEY_SLASH)
	KeySemicolon = 		Key(pygame.K_SEMICOLON, 	glfw.KEY_SEMICOLON)
	KeyLeftBracket = 	Key(pygame.K_LEFTBRACKET, 	glfw.KEY_LEFT_BRACKET)
	KeyRightBracket = 	Key(pygame.K_RIGHTBRACKET, 	glfw.KEY_RIGHT_BRACKET)
	KeyBackslash = 		Key(pygame.K_BACKSLASH, 	glfw.KEY_BACKSLASH)
	KeyGrave = 			Key(pygame.K_BACKQUOTE, 	glfw.KEY_GRAVE_ACCENT)
	KeyEscape = 		Key(pygame.K_ESCAPE, 		glfw.KEY_ESCAPE)
	KeyEnter = 			Key(pygame.K_RETURN, 		glfw.KEY_ENTER)
	KeyTab = 			Key(pygame.K_TAB, 			glfw.KEY_TAB)
	KeyBackspace = 		Key(pygame.K_BACKSPACE, 	glfw.KEY_BACKSPACE)
	KeyInsert = 		Key(pygame.K_INSERT, 		glfw.KEY_INSERT)
	KeyDelete = 		Key(pygame.K_DELETE, 		glfw.KEY_DELETE)
	KeyPageUp = 		Key(pygame.K_PAGEUP, 		glfw.KEY_PAGE_UP)
	KeyPageDown = 		Key(pygame.K_PAGEDOWN, 		glfw.KEY_PAGE_DOWN)
	KeyHome = 			Key(pygame.K_HOME, 			glfw.KEY_HOME)
	KeyEnd = 			Key(pygame.K_END, 			glfw.KEY_END)
	KeyCapsLock = 		Key(pygame.K_CAPSLOCK, 		glfw.KEY_CAPS_LOCK)
	KeyScrollLock = 	Key(pygame.K_SCROLLOCK, 	glfw.KEY_SCROLL_LOCK)
	KeyNumLock = 		Key(pygame.K_NUMLOCK, 		glfw.KEY_NUM_LOCK)
	KeyPrintScreen = 	Key(pygame.K_PRINT, 		glfw.KEY_PRINT_SCREEN)
	KeyPause = 			Key(pygame.K_PAUSE, 		glfw.KEY_PAUSE)
	KeyMenu = 			Key(pygame.K_HOME, 			glfw.KEY_MENU)
	#functional
	KeyF1 = 			Key(pygame.K_F1, 			glfw.KEY_F1)
	KeyF2 = 			Key(pygame.K_F2, 			glfw.KEY_F2)
	KeyF3 = 			Key(pygame.K_F3, 			glfw.KEY_F3)
	KeyF4 = 			Key(pygame.K_F4, 			glfw.KEY_F4)
	KeyF5 = 			Key(pygame.K_F5, 			glfw.KEY_F5)
	KeyF6 = 			Key(pygame.K_F6, 			glfw.KEY_F6)
	KeyF7 = 			Key(pygame.K_F7, 			glfw.KEY_F7)
	KeyF8 = 			Key(pygame.K_F8, 			glfw.KEY_F8)
	KeyF9 = 			Key(pygame.K_F9, 			glfw.KEY_F9)
	KeyF10 = 			Key(pygame.K_F10, 			glfw.KEY_F10)
	KeyF11 = 			Key(pygame.K_F11, 			glfw.KEY_F11)
	KeyF12 = 			Key(pygame.K_F12, 			glfw.KEY_F12)
	#modifiers
	KeyLeftShift = 		Key(pygame.K_LSHIFT, 		glfw.KEY_LEFT_SHIFT)
	KeyRightShift = 	Key(pygame.K_RSHIFT, 		glfw.KEY_RIGHT_SHIFT)
	KeyLeftControl = 	Key(pygame.K_LCTRL, 		glfw.KEY_LEFT_CONTROL)
	KeyRightControl = 	Key(pygame.K_RCTRL, 		glfw.KEY_RIGHT_CONTROL)
	KeyLeftAlt = 		Key(pygame.K_LALT, 			glfw.KEY_LEFT_ALT)
	KeyRightAlt = 		Key(pygame.K_RALT, 			glfw.KEY_RIGHT_ALT)
	KeyLeftSuper = 		Key(pygame.K_LSUPER, 		glfw.KEY_LEFT_SUPER)
	KeyRightSuper = 	Key(pygame.K_RSUPER, 		glfw.KEY_RIGHT_SUPER)
	#arrows
	KeyRight = 			Key(pygame.K_RIGHT, 		glfw.KEY_RIGHT)
	KeyLeft = 			Key(pygame.K_LEFT, 			glfw.KEY_LEFT)
	KeyUp = 			Key(pygame.K_UP, 			glfw.KEY_UP)
	KeyDown = 			Key(pygame.K_DOWN, 			glfw.KEY_DOWN)
	#numerical
	Key0 = 				Key(pygame.K_0, 			glfw.KEY_0)
	Key1 = 				Key(pygame.K_1, 			glfw.KEY_1)
	Key2 = 				Key(pygame.K_2, 			glfw.KEY_2)
	Key3 = 				Key(pygame.K_3, 			glfw.KEY_3)
	Key4 = 				Key(pygame.K_4, 			glfw.KEY_4)
	Key5 = 				Key(pygame.K_5, 			glfw.KEY_5)
	Key6 = 				Key(pygame.K_6, 			glfw.KEY_6)
	Key7 = 				Key(pygame.K_7, 			glfw.KEY_7)
	Key8 = 				Key(pygame.K_8, 			glfw.KEY_8)
	Key9 = 				Key(pygame.K_9, 			glfw.KEY_9)
	#alphabetical
	KeyA = 				Key(pygame.K_a, 			glfw.KEY_A)
	KeyB = 				Key(pygame.K_b, 			glfw.KEY_B)
	KeyC = 				Key(pygame.K_c, 			glfw.KEY_C)
	KeyD = 				Key(pygame.K_d, 			glfw.KEY_D)
	KeyE = 				Key(pygame.K_e, 			glfw.KEY_E)
	KeyF = 				Key(pygame.K_f, 			glfw.KEY_F)
	KeyG = 				Key(pygame.K_g, 			glfw.KEY_G)
	KeyH = 				Key(pygame.K_h, 			glfw.KEY_H)
	KeyI = 				Key(pygame.K_i, 			glfw.KEY_I)
	KeyJ = 				Key(pygame.K_j, 			glfw.KEY_J)
	KeyK = 				Key(pygame.K_k, 			glfw.KEY_K)
	KeyL = 				Key(pygame.K_l, 			glfw.KEY_L)
	KeyM = 				Key(pygame.K_m, 			glfw.KEY_M)
	KeyN = 				Key(pygame.K_n, 			glfw.KEY_N)
	KeyO = 				Key(pygame.K_o, 			glfw.KEY_O)
	KeyP = 				Key(pygame.K_p, 			glfw.KEY_P)
	KeyQ = 				Key(pygame.K_q, 			glfw.KEY_Q)
	KeyR = 				Key(pygame.K_r, 			glfw.KEY_R)
	KeyS = 				Key(pygame.K_s, 			glfw.KEY_S)
	KeyT = 				Key(pygame.K_t, 			glfw.KEY_T)
	KeyU = 				Key(pygame.K_u, 			glfw.KEY_U)
	KeyV = 				Key(pygame.K_v, 			glfw.KEY_V)
	KeyW = 				Key(pygame.K_w, 			glfw.KEY_W)
	KeyX = 				Key(pygame.K_x, 			glfw.KEY_X)
	KeyY = 				Key(pygame.K_y, 			glfw.KEY_Y)
	KeyZ = 				Key(pygame.K_z, 			glfw.KEY_Z)