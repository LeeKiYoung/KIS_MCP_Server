# 한국투자증권 REST API MCP (Model Context Protocol)

한국투자증권(KIS)의 REST API를 사용하여 주식 거래 및 시세 정보를 조회하는 MCP(Model Context Protocol) 서버입니다. 국내 및 해외 주식 거래, 시세 조회, 계좌 관리 등 다양한 금융 거래 기능을 제공합니다.

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
.venv\Scripts\activate  # Windows

# 3. Install dependencies
uv pip install -e .

# 4. Set environment variables
export KIS_APP_KEY="앱키"
export KIS_APP_SECRET="시크릿키"
export KIS_ACCOUNT_TYPE="VIRTUAL"  # 또는 "REAL"
export KIS_CANO="계좌번호"
```

## Project Structure

```
kis-mcp-server/
├── pyproject.toml        # Project metadata and dependencies
├── README.md            # Project documentation
├── main.py             # Main MCP server implementation
└── client.py           # Client implementation and examples
```

## Development

### Dependencies Management

이 프로젝트는 `uv`를 사용하여 의존성을 관리합니다. 새로운 패키지를 추가하려면:

```bash
# 프로덕션 의존성 추가
uv pip install package-name

# 개발 의존성 추가
uv pip install --dev package-name

# 의존성 업데이트
uv pip compile pyproject.toml
```
## Functions

### Domestic Stock Trading

* **order_stock** - 국내 주식 매수/매도 주문
  * `symbol`: 종목코드 (예: "005930") (string, required)
  * `quantity`: 주문수량 (number, required)
  * `price`: 주문가격 (0: 시장가) (number, required)
  * `order_type`: 주문유형 ("buy" 또는 "sell") (string, required)

* **inquery_stock_price** - 실시간 현재가 조회
  * `symbol`: 종목코드 (string, required)
  * Returns: 현재가, 전일대비, 등락률, 거래량 등

* **inquery_balance** - 계좌 잔고 조회
  * Returns: 보유종목, 평가금액, 손익현황 등

* **inquery_order_list** - 일별 주문 내역 조회
  * `start_date`: 조회 시작일 (YYYYMMDD) (string, required)
  * `end_date`: 조회 종료일 (YYYYMMDD) (string, required)

* **inquery_order_detail** - 주문 상세 내역 조회
  * `order_no`: 주문번호 (string, required)
  * `order_date`: 주문일자 (YYYYMMDD) (string, required)

### Overseas Stock Trading

* **order_overseas_stock** - 해외 주식 매수/매도 주문
  * `symbol`: 종목코드 (예: "AAPL") (string, required)
  * `quantity`: 주문수량 (number, required)
  * `price`: 주문가격 (number, required)
  * `order_type`: 주문유형 ("buy" 또는 "sell") (string, required)
  * `market`: 시장코드 (string, required)
    * "NASD": 나스닥
    * "NYSE": 뉴욕
    * "AMEX": 아멕스
    * "SEHK": 홍콩
    * "SHAA": 중국상해
    * "SZAA": 중국심천
    * "TKSE": 일본
    * "HASE": 베트남 하노이
    * "VNSE": 베트남 호치민

* **inquery_overseas_stock_price** - 해외 주식 현재가 조회
  * `symbol`: 종목코드 (string, required)
  * `market`: 시장코드 (string, required)

### Market Information

* **inquery_stock_info** - 일별 주가 정보 조회
  * `symbol`: 종목코드 (string, required)
  * `start_date`: 조회 시작일 (YYYYMMDD) (string, required)
  * `end_date`: 조회 종료일 (YYYYMMDD) (string, required)

* **inquery_stock_history** - 주가 히스토리 조회
  * `symbol`: 종목코드 (string, required)
  * `start_date`: 조회 시작일 (YYYYMMDD) (string, required)
  * `end_date`: 조회 종료일 (YYYYMMDD) (string, required)

* **inquery_stock_ask** - 호가 정보 조회
  * `symbol`: 종목코드 (string, required)

## Resources

### Configuration

* **Environment Variables**
  * **Template**: `.env` 파일 또는 환경변수 설정
  * **Parameters**:
    * `KIS_APP_KEY`: API 앱키 (string, required)
    * `KIS_APP_SECRET`: API 시크릿키 (string, required)
    * `KIS_ACCOUNT_TYPE`: 계정타입 ("REAL" 또는 "VIRTUAL") (string, required)
    * `KIS_CANO`: 계좌번호 (string, required)

### Trading Hours

* **Domestic Market**
  * 정규장: 09:00 ~ 15:30
  * 시간외 단일가:
    * 장 개시 전: 08:30 ~ 09:00
    * 장 종료 후: 15:40 ~ 16:00

* **Overseas Market**
  * 각 시장별 거래시간 준수
  * 휴장일 거래 불가

## Library Usage

```python
# 1. 주식 현재가 조회
result = await inquery_stock_price(symbol="005930")
print(f"현재가: {result['stck_prpr']}")
print(f"전일대비: {result['prdy_vrss']} ({result['prdy_ctrt']}%)")

# 2. 주식 매수 주문
result = await order_stock(
    symbol="005930",
    quantity=1,
    price=0,  # 시장가 주문
    order_type="buy"
)

# 3. 해외주식 매수 주문
result = await order_overseas_stock(
    symbol="AAPL",
    quantity=1,
    price=150.00,
    order_type="buy",
    market="NASD"
)
```

## Error Handling

### Error Codes
* `20010000`: 요청 성공
* `40580000`: 모의투자 장종료
* `40010001`: 주문가능 시간이 아님
* `40010002`: 잔고 부족

### Best Practices
* 모든 API 호출은 try-catch로 감싸서 사용
* 에러 발생 시 응답의 msg1 필드 확인
* 주문 실패 시 error_description 필드 확인

## About

이 프로젝트는 한국투자증권의 공식 REST API를 사용하여 개발된 MCP 서버입니다. 비동기 처리를 지원하며, 자동 토큰 갱신 및 에러 핸들링 기능을 제공합니다.

### Features
* 비동기 처리 지원 (asyncio 기반)
* 자동 토큰 갱신
* 체계적인 에러 핸들링
* 모듈화된 구조
* 확장 가능한 설계

### License
이 프로젝트는 MIT 라이선스 하에 제공됩니다.



