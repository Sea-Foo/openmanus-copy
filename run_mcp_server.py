
from src.mcp.server import MCPServer, parse_args

if __name__ == "__main__":
    args = parse_args()

    # Create and run server (maintaining original flow)
    server = MCPServer()
    server.run(transport=args.transport)