class branch:
    'Data class for a branch'

    def __init__(self, date, text, ID):
        self.date = date
        self.text = text
        self.ID = ID

    def __str__(self):
        return "Story text:" + self.text