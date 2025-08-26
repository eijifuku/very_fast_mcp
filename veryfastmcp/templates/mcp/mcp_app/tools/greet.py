class GreetTool:
    name = "greet"
    description = "Greet someone."

    async def run(self, inp: dict) -> dict:
        name = inp.get("name", "World")
        return {"message": f"Hello, {name}!"}
