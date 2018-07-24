class Menu:

    def __init__(self, sp):
        self.title = ""
        self.options = []
        self.sp = sp

    def set_title(self, title):
        self.title = title

    def set_options(self, options):
        self.options = options

    def show(self):
        print(self.title)
        self.options.append("None")
        for option in self.options:
            try:
                print("[{}] {}".format(self.options.index(option)+1, option.album_by_artist()))
            except AttributeError:
                print("[{}] {}\n".format(self.options.index(option)+1, option))
        while True:
            try:
                choice = int(input(">> ")) - 1
                chosen = self.options[choice]
                if chosen == "None":
                    return
                self.options[choice].add_to_spotify(self.sp)
                break
            except (IndexError, ValueError):
                print("Please enter a valid choice")
