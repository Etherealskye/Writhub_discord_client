class story:
    'Data class for a story'

    def __init__(self,title, date, text, description):
        self.title = title
        self.date = date
        self.text = text
        self.description = description

    def __str__(self):
        return "Story title:" + self.title