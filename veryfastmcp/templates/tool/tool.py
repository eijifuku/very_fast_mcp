class {{ class_base }}Tool:
    name = "{{ tool_name }}"
    description = "Run a {{ tool_name }} query."

    async def run(self, inp: dict) -> dict:
        # TODO: implement your business logic here
        return {"results": ["example"]}
