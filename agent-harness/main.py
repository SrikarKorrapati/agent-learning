from dotenv import load_dotenv

from harness import AgentHarness


load_dotenv()

harness = AgentHarness()
active_skill = None

print("Agent harness")
print("Commands:")
print("  /skills")
print("  /skill <name>")
print("  /remember <key>=<value>")
print("  /agents <task 1> | <task 2>")
print("  /exit")


while True:
    user_input = input("\nYou: ").strip()

    if user_input == "/exit":
        break

    if user_input == "/skills":
        print(harness.available_skills())
        continue

    if user_input.startswith("/skill "):
        active_skill = user_input.removeprefix("/skill ").strip()
        print(f"Active skill: {active_skill}")
        continue

    if user_input.startswith("/remember "):
        memory = user_input.removeprefix("/remember ")
        key, value = memory.split("=", 1)
        harness.remember(key.strip(), value.strip())
        print("Memory saved.")
        continue

    if user_input.startswith("/agents "):
        tasks = [
            task.strip()
            for task in user_input.removeprefix("/agents ").split("|")
        ]

        result = harness.run_subagents(tasks)

        print("\nSubagent results:")
        for item in result["subagent_results"]:
            print(f"- {item['task']}: {item['result']}")

        print("\nRoot agent:")
        print(result["final_answer"])
        continue

    answer = harness.ask(
        user_input,
        session_id="user-1",
        skill_name=active_skill,
    )

    print(f"\nAgent: {answer}")


harness.close()

