import argparse
import sys
import json
from pathlib import Path

# Add the parent directory to sys.path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))
from codex import CodexDatabase

def get_db():
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    return CodexDatabase(str(data_dir / "codex.db"), str(data_dir / "chroma"))

def main():
    parser = argparse.ArgumentParser(description="Nebula-Writer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Entity Commands
    entity_parser = subparsers.add_parser("entity", help="Manage entities")
    entity_subparsers = entity_parser.add_subparsers(dest="entity_command", help="Entity actions")

    # Entity List
    entity_subparsers.add_parser("list", help="List all entities")

    # Entity Add
    entity_add = entity_subparsers.add_parser("add", help="Add a new entity")
    entity_add.add_argument("--name", required=True, help="Entity name")
    entity_add.add_argument("--type", required=True, choices=['character', 'location', 'item'], help="Entity type")
    entity_add.add_argument("--desc", help="Description")

    # Visualize Command
    visualize_parser = subparsers.add_parser("visualize", help="Visualize data")
    visualize_parser.add_argument("--format", required=True, choices=['mermaid'], help="Format of the visualization")

    # Write Command
    write_parser = subparsers.add_parser("write", help="Write a chapter using agentic workflow")
    write_parser.add_argument("--beat", required=True, help="The narrative beat to write")
    write_parser.add_argument("--words", type=int, default=500, help="Target word count")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    db = get_db()

    if args.command == "entity":
        if args.entity_command == "list":
            entities = db.get_entities()
            for e in entities:
                print(f"[{e['id']}] {e['name']} ({e['type']})")
        elif args.entity_command == "add":
            entity_id = db.add_entity(name=args.name, entity_type=args.type, description=args.desc)
            print(f"Added {args.type} '{args.name}' with ID: {entity_id}")
        else:
            entity_parser.print_help()

    elif args.command == "visualize":
        if args.format == "mermaid":
            relationships = db.get_relationships()
            entities = db.get_entities()
            entity_map = {e['id']: e for e in entities}

            print("graph TD")
            for rel in relationships:
                from_name = entity_map[rel['from_entity_id']]['name'].replace(" ", "_")
                to_name = entity_map[rel['to_entity_id']]['name'].replace(" ", "_")
                rel_type = rel['relationship_type']
                print(f"    {from_name} -->|{rel_type}| {to_name}")

    elif args.command == "write":
        import os
        if not os.environ.get("GEMINI_API_KEY"):
            print("Error: Please set the GEMINI_API_KEY environment variable to use the LLM feature.")
            sys.exit(1)

        sys.path.insert(0, str(Path(__file__).parent))
        from llm import generate_prose

        print(f"Retrieving memory context for beat: '{args.beat}'...")
        context = db.search_memory(args.beat, n_results=3)
        stats = db.get_stats()

        print("Generating prose using Gemini API...")
        prose = generate_prose(args.beat, context, stats)

        print("\n--- GENERATED PROSE ---\n")
        print(prose)
        print("\n-----------------------\n")

if __name__ == "__main__":
    main()
