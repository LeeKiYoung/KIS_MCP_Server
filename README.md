# 한국투자증권 REST API MCP (Model Context Protocol)

- 한국투자증권(KIS)의 REST API를 사용하여 해외 시세 정보를 조회하는 MCP(Model Context Protocol) 서버입니다.
- Fork by: https://github.com/migusdn/KIS_MCP_Server

## Requirements

* Python >= 3.13
* uv (Python packaging tool)

## Installation

```bash
# 1. Install uv if not already installed
pip install uv

# 2. Create and activate virtual environment
uv venv
source .venv/bin/activate  # Linux/MacOS
# or
.venv\\Scripts\\activate  # Windows

# 3. Install dependencies
uv pip install -e .

mcp install server.py \
    -v KIS_APP_KEY={KIS_APP_KEY} \
    -v KIS_APP_SECRET={KIS_APP_SECRET} \
    -v KIS_ACCOUNT_TYPE={KIS_ACCOUNT_TYPE} \
    -v KIS_CANO={KIS_CANO}
```

### MCP Server Configuration

You can also configure the MCP server using a JSON configuration file. Create a file named `mcp-config.json` with the following content (replace the paths and environment variables with your own):

```json
{
  "mcpServers": {
    "KIS MCP Server": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "run",
        "--with",
        "httpx",
        "--with",
        "mcp[cli]",
        "--with",
        "xmltodict",
        "mcp",
        "run",
        "/path/to/your/project/server.py"
      ],
      "env": {
        "KIS_APP_KEY": "your_app_key",
        "KIS_APP_SECRET": "your_secret_key",
        "KIS_ACCOUNT_TYPE": "REAL",
        "KIS_CANO": "your_account_number"
      }
    }
  }
}
```

This configuration can be used with MCP-compatible tools and IDEs to run the server with the specified dependencies and environment variables.

## Functions

### Overseas Stock Method 참고

* https://github.com/koreainvestment/open-trading-api/blob/main/examples_user/overseas_stock/overseas_stock_functions.py

## Resources

### Configuration

환경 변수를 통해 API 키와 계좌 정보를 설정합니다:

* `KIS_APP_KEY`: 한국투자증권 앱키
* `KIS_APP_SECRET`: 한국투자증권 시크릿키
* `KIS_ACCOUNT_TYPE`: 계좌 타입 ("REAL" 또는 "VIRTUAL")
* `KIS_CANO`: 계좌번호

### Trading Hours

해외 주식:
* 미국(나스닥/뉴욕): 22:30 ~ 05:00 (한국시간)
* 일본: 09:00 ~ 15:10
* 중국: 10:30 ~ 16:00
* 홍콩: 10:30 ~ 16:00
* 베트남: 11:15 ~ 16:15

## License

MIT License
