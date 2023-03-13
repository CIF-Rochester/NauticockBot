class GivePointsOutput:
    createdEvent = False
    success = [str]
    failed = [str]

    def __init__(self, createdevent: bool, success: list[str], failed: list[str]):
        self.createdEvent = createdevent
        self.success = success
        self.failed = failed

    def discord_format(self) -> str:
        out = ""
        if self.createdEvent:
            out += "**Did create event.**\n"
        if len(self.success) > 0:
            out += "\n**Successfully gave points to**\n"
            for x in range(len(self.success)):
                out += self.success[x]
                out += "\n"
        if len(self.failed) > 0:
            out += "\n**Failures caused by**\n"
            for x in range(len(self.failed)):
                out += self.failed[x]
                out += "\n"
        return out
