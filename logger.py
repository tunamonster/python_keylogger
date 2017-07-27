from pynput_local import keyboard
import time
import pickle
import os

class Config():
    buffer_size = 4000
    pickle_size = 20000
    log_path = './logs/'
    allowed_modifiers = ['Key.cmd', 'Key.alt', 'Key.ctrl', 'Key.shift' ]

class KeyProcessor():
    def __init__(self, config):
        self.config = config
        self.key_buffer = []
        self.modifiers = set()

    def append_keys(self, old_log):
        new_history = {
            "key_history": old_log["key_history"] + self.key_buffer
        }   
        pickle.dump(new_history, open(self.last_log(), "wb"))

    def size_exceeded(self, file):
        exceeded = True if len(file["key_history"]) > self.config.pickle_size else False
        return exceeded

    def save_and_reset(self):
        loaded_log = pickle.load(open( self.last_log(), "rb" ))
        if self.size_exceeded(loaded_log):
            self.make_new_log(self.key_buffer)
        else:
            self.append_keys(loaded_log)
        self.key_buffer = []

    def save_to_key_buffer(self, key):
        timestamp = time.time()
        self.key_buffer.append([timestamp, key])
        if len(self.key_buffer) > self.config.buffer_size:
            self.save_and_reset()

    def process_keydown(self, key):
        if key in self.config.allowed_modifiers:
            self.modifiers.add(key)
        else:
            keystroke = list(self.modifiers) + [key]
            self.save_to_key_buffer(keystroke)

    def process_keyup(self, key):
        if key in self.modifiers:
            self.modifiers.remove(key)

    def on_press(self, key):
        try:
            self.process_keydown(key.char)
        except AttributeError:
            self.process_keydown(str(key))
            
    def on_release(self, key):
        try:
            self.process_keyup(key.char)
        except AttributeError:
            self.process_keyup(str(key))

    def last_log(self):
        all_files = self.get_log_files()
        last_file_path = self.config.log_path + all_files[-1]
        return last_file_path

    def get_log_files(self):
        try:
            files = os.listdir(self.config.log_path)
        except FileNotFoundError:
            os.mkdir(self.config.log_path)
            files = os.listdir(self.config.log_path)
        return files

    def make_new_log(self, first_inputs=list()):
        timestamp = int(time.time())
        new_dict = {
            'key_history': first_inputs
        }
        file_name = "{}.p".format(self.config.log_path + str(timestamp))
        pickle.dump( new_dict, open(file_name, "wb" ) )

    def log_check(self):
        files = self.get_log_files()
        if not files or files == ['.DS_Store']:
            self.make_new_log()

config = Config()
kp = KeyProcessor(config)
kp.log_check()

try:
    with keyboard.Listener(
            on_press=kp.on_press,
            on_release=kp.on_release) as listener:
        listener.join()
except (KeyboardInterrupt, SystemExit):
    print('buffer size: {}'.format(len(kp.key_buffer)))
    print('saving to {} ...'.format(kp.last_log))
    kp.save_and_reset()
    print('succesfully saved! exiting program')



# on exit    