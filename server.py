import json
import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

import httpx
from mcp.server.fastmcp.server import FastMCP

# 로깅 설정: 반드시 stderr로 출력
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger("mcp-server")

# Create MCP instance
mcp = FastMCP("KIS MCP Server", dependencies=["httpx", "xmltodict"])

# Load environment variables from .env file
load_dotenv()

# Global strings for API endpoints and paths
DOMAIN = "https://openapi.koreainvestment.com:9443"
VIRTUAL_DOMAIN = "https://openapivts.koreainvestment.com:29443"  # 모의투자

# API paths
TOKEN_PATH = "/oauth2/tokenP"  # 토큰발급
HASHKEY_PATH = "/uapi/hashkey"  # 해시키발급

# Headers and other constants
CONTENT_TYPE = "application/json"
AUTH_TYPE = "Bearer"

# Market codes for overseas stock
MARKET_CODES = {
    "NASD": "나스닥",
    "NYSE": "뉴욕",
    "AMEX": "아멕스",
    "SEHK": "홍콩",
    "SHAA": "중국상해",
    "SZAA": "중국심천",
    "TKSE": "일본",
    "HASE": "베트남 하노이",
    "VNSE": "베트남 호치민"
}

class TrIdManager:
    """Transaction ID manager for Korea Investment & Securities API"""
    
    # 실전계좌용 TR_ID
    REAL = {
        # 국내주식
        "balance": "TTTC8434R",  # 잔고조회
        "price": "FHKST01010100",  # 현재가조회
        "buy": "TTTC0802U",  # 주식매수
        "sell": "TTTC0801U",  # 주식매도
        "order_list": "TTTC8001R",  # 일별주문체결조회
        "order_detail": "TTTC8036R",  # 주문체결내역조회
        "stock_info": "FHKST01010400",  # 일별주가조회
        "stock_history": "FHKST03010200",  # 주식일별주가조회
        "stock_ask": "FHKST01010200",  # 주식호가조회
        
        # 해외주식
        "us_buy": "TTTT1002U",      # 미국 매수 주문
        "us_sell": "TTTT1006U",     # 미국 매도 주문
        "jp_buy": "TTTS0308U",      # 일본 매수 주문
        "jp_sell": "TTTS0307U",     # 일본 매도 주문
        "sh_buy": "TTTS0202U",      # 상해 매수 주문
        "sh_sell": "TTTS1005U",     # 상해 매도 주문
        "hk_buy": "TTTS1002U",      # 홍콩 매수 주문
        "hk_sell": "TTTS1001U",     # 홍콩 매도 주문
        "sz_buy": "TTTS0305U",      # 심천 매수 주문
        "sz_sell": "TTTS0304U",     # 심천 매도 주문
        "vn_buy": "TTTS0311U",      # 베트남 매수 주문
        "vn_sell": "TTTS0310U",     # 베트남 매도 주문
    }
    
    # 모의계좌용 TR_ID
    VIRTUAL = {
        # 국내주식
        "balance": "VTTC8434R",  # 잔고조회
        "price": "FHKST01010100",  # 현재가조회
        "buy": "VTTC0802U",  # 주식매수
        "sell": "VTTC0801U",  # 주식매도
        "order_list": "VTTC8001R",  # 일별주문체결조회
        "order_detail": "VTTC8036R",  # 주문체결내역조회
        "stock_info": "FHKST01010400",  # 일별주가조회
        "stock_history": "FHKST03010200",  # 주식일별주가조회
        "stock_ask": "FHKST01010200",  # 주식호가조회
        
        # 해외주식
        "us_buy": "VTTT1002U",      # 미국 매수 주문
        "us_sell": "VTTT1001U",     # 미국 매도 주문
        "jp_buy": "VTTS0308U",      # 일본 매수 주문
        "jp_sell": "VTTS0307U",     # 일본 매도 주문
        "sh_buy": "VTTS0202U",      # 상해 매수 주문
        "sh_sell": "VTTS1005U",     # 상해 매도 주문
        "hk_buy": "VTTS1002U",      # 홍콩 매수 주문
        "hk_sell": "VTTS1001U",     # 홍콩 매도 주문
        "sz_buy": "VTTS0305U",      # 심천 매수 주문
        "sz_sell": "VTTS0304U",     # 심천 매도 주문
        "vn_buy": "VTTS0311U",      # 베트남 매수 주문
        "vn_sell": "VTTS0310U",     # 베트남 매도 주문
    }
    
    @classmethod
    def get_tr_id(cls, operation: str) -> str:
        """
        Get transaction ID for the given operation
        
        Args:
            operation: Operation type ('balance', 'price', 'buy', 'sell', etc.)
            
        Returns:
            str: Transaction ID for the operation
        """
        is_real_account = os.environ.get("KIS_ACCOUNT_TYPE", "REAL").upper() == "REAL"
        tr_id_map = cls.REAL if is_real_account else cls.VIRTUAL
        return tr_id_map.get(operation)
    
    @classmethod
    def get_domain(cls, operation: str) -> str:
        """
        Get domain for the given operation
        
        Args:
            operation: Operation type ('balance', 'price', 'buy', 'sell', etc.)
            
        Returns:
            str: Domain URL for the operation
        """
        is_real_account = os.environ.get("KIS_ACCOUNT_TYPE", "REAL").upper() == "REAL"
        
        # 잔고조회는 실전/모의 계좌별로 다른 도메인 사용
        if operation == "balance":
            return DOMAIN if is_real_account else VIRTUAL_DOMAIN
            
        # 조회 API는 실전/모의 동일한 도메인 사용
        if operation in ["price", "stock_info", "stock_history", "stock_ask"]:
            return DOMAIN
            
        # 거래 API는 계좌 타입에 따라 다른 도메인 사용
        return DOMAIN if is_real_account else VIRTUAL_DOMAIN

# Token storage
TOKEN_FILE = Path(__file__).resolve().parent / "token.json"

def load_token():
    """Load token from file if it exists and is not expired"""
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
                expires_at = datetime.fromisoformat(token_data['expires_at'])
                if datetime.now() < expires_at:
                    return token_data['token'], expires_at
        except Exception as e:
            print(f"Error loading token: {e}", file=sys.stderr)
    return None, None

def save_token(token: str, expires_at: datetime):
    """Save token to file"""
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump({
                'token': token,
                'expires_at': expires_at.isoformat()
            }, f)
    except Exception as e:
        print(f"Error saving token: {e}", file=sys.stderr)

async def get_access_token(client: httpx.AsyncClient) -> str:
    """
    Get access token with file-based caching
    Returns cached token if valid, otherwise requests new token
    """
    token, expires_at = load_token()
    if token and expires_at and datetime.now() < expires_at:
        return token
    
    token_response = await client.post(
        f"{DOMAIN}{TOKEN_PATH}",
        headers={"content-type": CONTENT_TYPE},
        json={
            "grant_type": "client_credentials",
            "appkey": os.environ["KIS_APP_KEY"],
            "appsecret": os.environ["KIS_APP_SECRET"]
        }
    )
    
    if token_response.status_code != 200:
        raise Exception(f"Failed to get token: {token_response.text}")
    
    token_data = token_response.json()
    token = token_data["access_token"]
    
    expires_at = datetime.now() + timedelta(hours=23)
    save_token(token, expires_at)
    
    return token

async def get_hashkey(client: httpx.AsyncClient, token: str, body: dict) -> str:
    """
    Get hash key for order request
    
    Args:
        client: httpx client
        token: Access token
        body: Request body
        
    Returns:
        str: Hash key
    """
    response = await client.post(
        f"{TrIdManager.get_domain('buy')}{HASHKEY_PATH}",
        headers={
            "content-type": CONTENT_TYPE,
            "authorization": f"{AUTH_TYPE} {token}",
            "appkey": os.environ["KIS_APP_KEY"],
            "appsecret": os.environ["KIS_APP_SECRET"],
        },
        json=body
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get hash key: {response.text}")
    
    return response.json()["HASH"]


@mcp.tool(
    name="period_rights",
    description="시세분석 > 해외주식 기간별권리조회",
    annotations={
        "rght_type_cd": {
            "type": "string",
            "required": True,
            "description": "권리유형코드",
            "examples": ["%%", "01", "02", "03"],
            "enum": ["%%:전체", "01:유상", "02:무상", "03:배당", "11:합병", "14:액면분할", "15:액면병합", "17:감자", "54:WR청구", "61:원리금상환", "71:WR소멸", "74:배당옵션", "75:특별배당", "76:ISINCODE변경", "77:실권주청약"]
        },
        "inqr_dvsn_cd": {
            "type": "string", 
            "required": True,
            "description": "조회구분코드",
            "examples": ["02", "03", "04"],
            "enum": ["02:현지기준일", "03:청약시작일", "04:청약종료일"]
        },
        "inqr_strt_dt": {
            "type": "string",
            "required": True,
            "description": "조회시작일자 (YYYYMMDD 형식)",
            "examples": ["20250101", "20240315"]
        },
        "inqr_end_dt": {
            "type": "string",
            "required": True,
            "description": "조회종료일자 (YYYYMMDD 형식)",
            "examples": ["20250131", "20240415"]
        },
        "pdno": {
            "type": "string",
            "required": False,
            "description": "상품번호 (선택사항)",
            "examples": [""]
        },
        "prdt_type_cd": {
            "type": "string",
            "required": False,
            "description": "상품유형코드 (선택사항)",
            "examples": [""]
        },
        "NK50": {
            "type": "string",
            "required": False,
            "description": "연속조회키50 (선택사항)",
            "examples": [""]
        },
        "FK50": {
            "type": "string",
            "required": False,
            "description": "연속조회검색조건50 (선택사항)",
            "examples": [""]
        }
    }
)
async def period_rights(
    rght_type_cd: str,  # 권리유형코드
    inqr_dvsn_cd: str,  # 조회구분코드
    inqr_strt_dt: str,  # 조회시작일자
    inqr_end_dt: str,  # 조회종료일자
    pdno: str = "",  # 상품번호
    prdt_type_cd: str = "",  # 상품유형코드
    NK50: str = "",  # 연속조회키50
    FK50: str = "",  # 연속조회검색조건50
):
    """
    해외주식 기간별권리조회 API입니다.
    한국투자 HTS(eFriend Plus) > [7520] 기간별해외증권권리조회 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    ※ 확정여부가 '예정'으로 표시되는 경우는 권리정보가 변경될 수 있으니 참고자료로만 활용하시기 바랍니다.

    Args:
        rght_type_cd (str): [필수] 권리유형코드 (%%:전체, 01:유상, 02:무상, 03:배당, 11:합병,14:액면분할, 15:액면병합, 17:감자, 54:WR청구,61:원리금상환, 71:WR소멸, 74:배당옵션, 75:특별배당, 76:ISINCODE변경, 77:실권주청약)
        inqr_dvsn_cd (str): [필수] 조회구분코드 (02:현지기준일, 03:청약시작일, 04:청약종료일)
        inqr_strt_dt (str): [필수] 조회시작일자 (20250101)
        inqr_end_dt (str): [필수] 조회종료일자 (20250131)
        pdno (str): 상품번호
        prdt_type_cd (str): 상품유형코드
        NK50 (str): 연속조회키50
        FK50 (str): 연속조회검색조건50

    Returns:
        pd.DataFrame: 해외주식 기간별권리조회 데이터
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        # 필수 파라미터 검증
        if rght_type_cd == "":
            raise ValueError(
                "rght_type_cd is required (e.g. '%%:전체, 01:유상, 02:무상, 03:배당, 11:합병,14:액면분할, 15:액면병합, 17:감자, 54:WR청구,61:원리금상환, 71:WR소멸, 74:배당옵션, 75:특별배당, 76:ISINCODE변경, 77:실권주청약')")

        if inqr_dvsn_cd == "":
            raise ValueError("inqr_dvsn_cd is required (e.g. '02:현지기준일, 03:청약시작일, 04:청약종료일')")

        if inqr_strt_dt == "":
            raise ValueError("inqr_strt_dt is required (e.g. '20250101')")

        if inqr_end_dt == "":
            raise ValueError("inqr_end_dt is required (e.g. '20250131')")

        tr_id = "CTRGT011R"  # 해외주식 기간별권리조회

        api_url = "/uapi/overseas-price/v1/quotations/period-rights"

        params = {
            "RGHT_TYPE_CD": rght_type_cd,  # 권리유형코드
            "INQR_DVSN_CD": inqr_dvsn_cd,  # 조회구분코드
            "INQR_STRT_DT": inqr_strt_dt,  # 조회시작일자
            "INQR_END_DT": inqr_end_dt,  # 조회종료일자
            "PDNO": pdno,  # 상품번호
            "PRDT_TYPE_CD": prdt_type_cd,  # 상품유형코드
            "CTX_AREA_NK50": NK50,  # 연속조회키50
            "CTX_AREA_FK50": FK50  # 연속조회검색조건50
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get 해외속보(제목): {response.text}")

        return response.json()

@mcp.tool(
    name="price",
    description="기본시세 > 해외주식 현재체결가",
    annotations={
        "auth": {
            "type": "string",
            "required": True,
            "description": "사용자권한정보 (빈 문자열로 설정)",
            "examples": [""]
        },
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소코드",
            "examples": ["NAS", "NYS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "symb": {
            "type": "string",
            "required": True,
            "description": "종목코드 (티커 심볼)",
            "examples": ["AAPL", "MSFT", "GOOGL", "TSLA"]
        }
    }
)
async def price(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
):
    """
    [해외주식] 기본시세
    해외주식 현재체결가[v1_해외주식-009]
    해외주식 현재체결가 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        auth (str): 사용자권한정보
        excd (str): 거래소코드 (예: "NAS")
        symb (str): 종목코드 (예: "AAPL")

    Returns:
        Optional[pd.DataFrame]: 해외주식 현재체결가 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        # 필수 파라미터 검증
        if not excd:
            logger.error("excd is required. (e.g. 'NAS')")
            raise ValueError("excd is required. (e.g. 'NAS')")

        if not symb:
            logger.error("symb is required. (e.g. 'AAPL')")
            raise ValueError("symb is required. (e.g. 'AAPL')")

        tr_id = "HHDFS00000300"

        api_url = "/uapi/overseas-price/v1/quotations/price"

        params = {
            "AUTH": auth,
            "EXCD": excd,
            "SYMB": symb,
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get 해외속보(제목): {response.text}")

        return response.json()
        
        if response.status_code != 200:
            raise Exception(f"Failed to get overseas stock price: {response.text}")
        
        return response.json()


@mcp.tool(
    name="brknews-title",
    description="시세분석 > 해외속보(제목)",
    annotations={
        "fid_news_ofer_entp_code": {
            "type": "string",
            "required": True,
            "description": "뉴스제공업체코드",
            "examples": ["0"],
            "enum": ["0:전체조회"]
        },
        "fid_cond_scr_div_code": {
            "type": "string",
            "required": True,
            "description": "조건화면분류코드",
            "examples": ["11801"]
        },
        "fid_cond_mrkt_cls_code": {
            "type": "string",
            "required": False,
            "description": "조건시장구분코드 (선택사항)",
            "examples": [""]
        },
        "fid_input_iscd": {
            "type": "string",
            "required": False,
            "description": "입력종목코드 (선택사항)",
            "examples": [""]
        },
        "fid_titl_cntt": {
            "type": "string",
            "required": False,
            "description": "제목내용 (선택사항)",
            "examples": [""]
        },
        "fid_input_date_1": {
            "type": "string",
            "required": False,
            "description": "입력날짜1 (선택사항, YYYYMMDD 형식)",
            "examples": ["", "20250101"]
        },
        "fid_input_hour_1": {
            "type": "string",
            "required": False,
            "description": "입력시각1 (선택사항, HHMMSS 형식)",
            "examples": ["", "120000"]
        },
        "fid_rank_sort_cls_code": {
            "type": "string",
            "required": False,
            "description": "순위정렬구분코드 (선택사항)",
            "examples": [""]
        },
        "fid_input_srno": {
            "type": "string",
            "required": False,
            "description": "입력일련번호 (선택사항)",
            "examples": [""]
        }
    }
)
async def brknews_title(
    fid_news_ofer_entp_code: str,  # [필수] 뉴스제공업체코드
    fid_cond_scr_div_code: str,  # [필수] 조건화면분류코드
    fid_cond_mrkt_cls_code: str = "",  # 조건시장구분코드
    fid_input_iscd: str = "",  # 입력종목코드
    fid_titl_cntt: str = "",  # 제목내용
    fid_input_date_1: str = "",  # 입력날짜1
    fid_input_hour_1: str = "",  # 입력시각1
    fid_rank_sort_cls_code: str = "",  # 순위정렬구분코드
    fid_input_srno: str = ""  # 입력일련번호
):
    """
    해외속보(제목) API입니다.
    한국투자 HTS(eFriend Plus) > [7704] 해외속보 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    최대 100건까지 조회 가능합니다.

    Args:
        fid_news_ofer_entp_code (str): [필수] 뉴스제공업체코드 (ex. 0:전체조회)
        fid_cond_scr_div_code (str): [필수] 조건화면분류코드 (ex. 11801)
        fid_cond_mrkt_cls_code (str): 조건시장구분코드
        fid_input_iscd (str): 입력종목코드
        fid_titl_cntt (str): 제목내용
        fid_input_date_1 (str): 입력날짜1
        fid_input_hour_1 (str): 입력시각1
        fid_rank_sort_cls_code (str): 순위정렬구분코드
        fid_input_srno (str): 입력일련번호

    Returns:
        pd.DataFrame: 해외속보(제목) 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        if fid_news_ofer_entp_code == "":
            raise ValueError("fid_news_ofer_entp_code is required (e.g. '0')")

        if fid_cond_scr_div_code == "":
            raise ValueError("fid_cond_scr_div_code is required (e.g. '11801')")

        tr_id = "FHKST01011801"

        api_url = "/uapi/overseas-price/v1/quotations/brknews-title"

        params = {
            "FID_NEWS_OFER_ENTP_CODE": fid_news_ofer_entp_code,
            "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
            "FID_COND_MRKT_CLS_CODE": fid_cond_mrkt_cls_code,
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_TITL_CNTT": fid_titl_cntt,
            "FID_INPUT_DATE_1": fid_input_date_1,
            "FID_INPUT_HOUR_1": fid_input_hour_1,
            "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
            "FID_INPUT_SRNO": fid_input_srno
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get 해외속보(제목): {response.text}")

        return response.json()


@mcp.tool(
    name="inquire-ccnl",
    description="기본시세 > 해외주식 체결추이",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "tday": {
            "type": "string",
            "required": True,
            "description": "당일전일구분",
            "examples": ["0", "1"],
            "enum": ["0:전일", "1:당일"]
        },
        "symb": {
            "type": "string",
            "required": True,
            "description": "종목코드 (해외종목코드)",
            "examples": ["TSLA", "AAPL", "MSFT"]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보 (선택사항)",
            "examples": [""]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF (선택사항)",
            "examples": [""]
        }
    }
)
async def inquire_ccnl(
    excd: str,         # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    tday: str,         # [필수] 당일전일구분 (ex. 0:전일, 1:당일)
    symb: str,         # [필수] 종목코드 (ex. 해외종목코드)
    auth: str = "",    # 사용자권한정보
    keyb: str = "",    # NEXT KEY BUFF
):
    """
    해외주식 체결추이 API입니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        tday (str): [필수] 당일전일구분 (ex. 0:전일, 1:당일)
        symb (str): [필수] 종목코드 (ex. 해외종목코드)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF

    Returns:
        pd.DataFrame: 해외주식 체결추이 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        if excd == "":
            raise ValueError("excd is required (e.g. 'NAS')")

        if tday == "":
            raise ValueError("tday is required (e.g. '0' or '1')")

        if symb == "":
            raise ValueError("symb is required (e.g. 'TSLA')")

        tr_id = "HHDFS76200300"

        api_url = "/uapi/overseas-price/v1/quotations/inquire-ccnl"

        params = {
            "EXCD": excd,
            "TDAY": tday,
            "SYMB": symb,
            "AUTH": auth,
            "KEYB": keyb
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get 해외주식 체결추이: {response.text}")

        return response.json()


@mcp.tool(
    name="price-detail",
    description="기본시세 > 해외주식 현재가상세",
    annotations={
        "auth": {
            "type": "string",
            "required": True,
            "description": "사용자권한정보 (빈 문자열로 설정)",
            "examples": [""]
        },
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "symb": {
            "type": "string",
            "required": True,
            "description": "종목코드 (티커 심볼)",
            "examples": ["TSLA", "AAPL", "MSFT", "GOOGL"]
        }
    }
)
async def price_detail(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소명
    symb: str,  # 종목코드
):
    """
    [해외주식] 기본시세
    해외주식 현재가상세[v1_해외주식-029]
    해외주식 현재가상세 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        auth (str): 사용자권한정보
        excd (str): 거래소명 (예: HKS, NYS, NAS, AMS, TSE, SHS, SZS, SHI, SZI, HSX, HNX, BAY, BAQ, BAA)
        symb (str): 종목코드

    Returns:
        Optional[pd.DataFrame]: 해외주식 현재가상세 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        # [필수 파라미터 검증]
        if not excd:
            logger.error("excd is required. (e.g. 'NAS')")
            raise ValueError("excd is required. (e.g. 'NAS')")
        if not symb:
            logger.error("symb is required. (e.g. 'TSLA')")
            raise ValueError("symb is required. (e.g. 'TSLA')")

        tr_id = "HHDFS76200200"

        api_url = "/uapi/overseas-price/v1/quotations/price-detail"

        params = {
            "AUTH": auth,
            "EXCD": excd,
            "SYMB": symb,
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get 해외주식 현재가상세: {response.text}")

        return response.json()


@mcp.tool(
    name="news-title",
    description="기본시세 > 해외주식 현재가상세",
    annotations={
        "info_gb": {
            "type": "string",
            "required": True,
            "description": "뉴스구분",
            "examples": ["", "1", "2"],
            "enum": ["공백:전체", "1:종목뉴스", "2:일반뉴스"]
        },
        "class_cd": {
            "type": "string",
            "required": True,
            "description": "중분류",
            "examples": ["", "01", "02", "03"]
        },
        "nation_cd": {
            "type": "string",
            "required": True,
            "description": "국가코드",
            "examples": ["", "CN", "HK", "US"],
            "enum": ["공백:전체", "CN:중국", "HK:홍콩", "US:미국", "JP:일본", "VN:베트남"]
        },
        "exchange_cd": {
            "type": "string",
            "required": True,
            "description": "거래소코드",
            "examples": ["", "NYS", "NAS", "AMS"]
        },
        "symb": {
            "type": "string",
            "required": True,
            "description": "종목코드 (티커 심볼)",
            "examples": ["", "AAPL", "MSFT", "TSLA"]
        },
        "data_dt": {
            "type": "string",
            "required": True,
            "description": "조회일자 (YYYYMMDD 형식)",
            "examples": ["", "20250101", "20240315"]
        },
        "data_tm": {
            "type": "string",
            "required": True,
            "description": "조회시간 (HHMMSS 형식)",
            "examples": ["", "120000", "093000"]
        },
        "cts": {
            "type": "string",
            "required": True,
            "description": "다음키 (연속조회용, 처음조회시 공백)",
            "examples": ["", "20241014120000001"]
        }
    }
)
async def news_title(
    info_gb: str = "",  # [필수] 뉴스구분
    class_cd: str = "",  # [필수] 중분류
    nation_cd: str = "",  # [필수] 국가코드 (ex. 공백:전체, CN:중국, HK:홍콩, US:미국)
    exchange_cd: str = "",  # [필수] 거래소코드
    symb: str = "",  # [필수] 종목코드
    data_dt: str = "",  # [필수] 조회일자
    data_tm: str = "",  # [필수] 조회시간
    cts: str = "",  # [필수] 다음키
):
    """
    해외뉴스종합(제목) API입니다.
    한국투자 HTS(eFriend Plus) > [7702] 해외뉴스종합 화면의 "우측 상단 뉴스목록" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

    Args:
        info_gb (str): [필수] 뉴스구분
        class_cd (str): [필수] 중분류
        nation_cd (str): [필수] 국가코드 (ex. 공백:전체, CN:중국, HK:홍콩, US:미국)
        exchange_cd (str): [필수] 거래소코드
        symb (str): [필수] 종목코드
        data_dt (str): [필수] 조회일자
        data_tm (str): [필수] 조회시간
        cts (str): [필수] 다음키

    Returns:
        pd.DataFrame: 해외뉴스종합(제목) 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        tr_id = "HHPSTH60100C1"  # 해외뉴스종합(제목)

        api_url = "/uapi/overseas-price/v1/quotations/news-title"

        params = {
            "INFO_GB": info_gb,  # 뉴스구분
            "CLASS_CD": class_cd,  # 중분류
            "NATION_CD": nation_cd,  # 국가코드
            "EXCHANGE_CD": exchange_cd,  # 거래소코드
            "SYMB": symb,  # 종목코드
            "DATA_DT": data_dt,  # 조회일자
            "DATA_TM": data_tm,  # 조회시간
            "CTS": cts  # 다음키
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get 해외뉴스종합(제목): {response.text}")

        return response.json()


@mcp.tool(
    name="inquire-time-itemchartprice",
    description="기본시세 > 해외주식분봉조회 데이터",
    annotations={
        "auth": {
            "type": "string",
            "required": True,
            "description": "사용자권한정보 (공백으로 입력)",
            "examples": [""]
        },
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소코드",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄", "BAY:뉴욕(주간)", "BAQ:나스닥(주간)", "BAA:아멕스(주간)"]
        },
        "symb": {
            "type": "string",
            "required": True,
            "description": "종목코드",
            "examples": ["TSLA", "AAPL", "MSFT"]
        },
        "nmin": {
            "type": "string",
            "required": True,
            "description": "분단위 (1: 1분봉, 2: 2분봉, 5: 5분봉 등)",
            "examples": ["1", "5", "15", "30"]
        },
        "pinc": {
            "type": "string",
            "required": True,
            "description": "전일포함여부",
            "examples": ["0", "1"],
            "enum": ["0:당일", "1:전일포함 (다음조회 시 반드시 1로 입력)"]
        },
        "next": {
            "type": "string",
            "required": True,
            "description": "다음여부",
            "examples": ["", "1"],
            "enum": ["공백:처음조회", "1:다음조회"]
        },
        "nrec": {
            "type": "string",
            "required": True,
            "description": "요청갯수 (최대 120)",
            "examples": ["120", "100", "50"]
        },
        "fill": {
            "type": "string",
            "required": True,
            "description": "미체결채움구분 (공백으로 입력)",
            "examples": [""]
        },
        "keyb": {
            "type": "string",
            "required": True,
            "description": "NEXT KEY BUFF (처음조회시 공백, 다음조회시 YYYYMMDDHHMMSS 형식)",
            "examples": ["", "20241014140100"]
        }
    }
)
async def inquire_time_itemchartprice(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
    nmin: str,  # 분간격
    pinc: str,  # 전일포함여부
    next: str,  # 다음여부
    nrec: str,  # 요청갯수
    fill: str,  # 미체결채움구분
    keyb: str,  # NEXT KEY BUFF
):
    """
    [해외주식] 기본시세
    해외주식분봉조회[v1_해외주식-030]
    해외주식분봉조회 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        auth (str): "" 공백으로 입력
        excd (str): NYS : 뉴욕 NAS : 나스닥 AMS : 아멕스  HKS : 홍콩 SHS : 상해  SZS : 심천 HSX : 호치민 HNX : 하노이 TSE : 도쿄   ※ 주간거래는 최대 1일치 분봉만 조회 가능 BAY : 뉴욕(주간) BAQ : 나스닥(주간) BAA : 아멕스(주간)
        symb (str): 종목코드(ex. TSLA)
        nmin (str): 분단위(1: 1분봉, 2: 2분봉, ...)
        pinc (str): 0:당일 1:전일포함 ※ 다음조회 시 반드시 "1"로 입력
        next (str): 처음조회 시, "" 공백 입력 다음조회 시, "1" 입력
        nrec (str): 레코드요청갯수 (최대 120)
        fill (str): "" 공백으로 입력
        keyb (str): 처음 조회 시, "" 공백 입력 다음 조회 시, 이전 조회 결과의 마지막 분봉 데이터를 이용하여, 1분 전 혹은 n분 전의 시간을 입력  (형식: YYYYMMDDHHMMSS, ex. 20241014140100)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식분봉조회 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        # [필수 파라미터 검증]
        if not excd:
            logger.error("excd is required. (e.g. 'NAS')")
            raise ValueError("excd is required. (e.g. 'NAS')")
        if not symb:
            logger.error("symb is required. (e.g. 'TSLA')")
            raise ValueError("symb is required. (e.g. 'TSLA')")
        if not nmin:
            logger.error("nmin is required. (e.g. '5')")
            raise ValueError("nmin is required. (e.g. '5')")
        if not pinc:
            logger.error("pinc is required. (e.g. '1')")
            raise ValueError("pinc is required. (e.g. '1')")
        if not nrec or int(nrec) > 120:
            logger.error("nrec is required. (e.g. '120', 최대120개)")
            raise ValueError("nrec is required. (e.g. '120', 최대120개)")

        tr_id = "HHDFS76950200"

        api_url = "/uapi/overseas-price/v1/quotations/inquire-time-itemchartprice"

        params = {
            "AUTH": auth,
            "EXCD": excd,
            "SYMB": symb,
            "NMIN": nmin,
            "PINC": pinc,
            "NEXT": next,
            "NREC": nrec,
            "FILL": fill,
            "KEYB": keyb,
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get 해외주식분봉조회 데이터: {response.text}")

        return response.json()


@mcp.tool(
    name="inquire-time-indexchartprice",
    description="기본시세 > 해외지수분봉조회 데이터",
    annotations={
        "fid_cond_mrkt_div_code": {
            "type": "string",
            "required": True,
            "description": "조건 시장 분류 코드",
            "examples": ["N", "X", "KX"],
            "enum": ["N:해외지수", "X:환율", "KX:원화환율"]
        },
        "fid_input_iscd": {
            "type": "string",
            "required": True,
            "description": "입력 종목코드 (지수 심볼)",
            "examples": ["SPX", "IXIC", "DJI", "NDX"]
        },
        "fid_hour_cls_code": {
            "type": "string",
            "required": True,
            "description": "시간 구분 코드",
            "examples": ["0", "1"],
            "enum": ["0:정규장", "1:시간외"]
        },
        "fid_pw_data_incu_yn": {
            "type": "string",
            "required": True,
            "description": "과거 데이터 포함 여부",
            "examples": ["Y", "N"],
            "enum": ["Y:포함", "N:미포함"]
        }
    }
)
async def inquire_time_indexchartprice(
    fid_cond_mrkt_div_code: str,  # 조건 시장 분류 코드
    fid_input_iscd: str,  # 입력 종목코드
    fid_hour_cls_code: str,  # 시간 구분 코드
    fid_pw_data_incu_yn: str,  # 과거 데이터 포함 여부
):
    """
    [해외주식] 기본시세
    해외지수분봉조회[v1_해외주식-031]
    해외지수분봉조회 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        fid_cond_mrkt_div_code (str): N 해외지수 X 환율 KX 원화환율
        fid_input_iscd (str): 종목번호(ex. TSLA)
        fid_hour_cls_code (str): 0: 정규장, 1: 시간외
        fid_pw_data_incu_yn (str): Y/N

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외지수분봉조회 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        # [필수 파라미터 검증]
        if not fid_cond_mrkt_div_code:
            logger.error("fid_cond_mrkt_div_code is required. (e.g. 'N')")
            raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'N')")
        if not fid_input_iscd:
            logger.error("fid_input_iscd is required. (e.g. 'SPX')")
            raise ValueError("fid_input_iscd is required. (e.g. 'SPX')")
        if not fid_hour_cls_code:
            logger.error("fid_hour_cls_code is required. (e.g. '0')")
            raise ValueError("fid_hour_cls_code is required. (e.g. '0')")
        if not fid_pw_data_incu_yn:
            logger.error("fid_pw_data_incu_yn is required. (e.g. 'Y')")
            raise ValueError("fid_pw_data_incu_yn is required. (e.g. 'Y')")

        tr_id = "FHKST03030200"

        api_url = "/uapi/overseas-price/v1/quotations/inquire-time-indexchartprice"

        params = {
            "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_HOUR_CLS_CODE": fid_hour_cls_code,
            "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get 해외지수분봉조회 데이터: {response.text}")

        return response.json()


@mcp.tool(
    name="inquire-search",
    description="시세분석 > 해외주식조건검색",
    annotations={
        "auth": {
            "type": "string",
            "required": True,
            "description": "사용자권한정보 (빈 문자열로 설정)",
            "examples": [""]
        },
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소코드",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "co_yn_pricecur": {
            "type": "string",
            "required": True,
            "description": "현재가선택조건 (해당조건 사용시: 1, 미사용시: 공백)",
            "examples": ["1", ""]
        },
        "co_st_pricecur": {
            "type": "string",
            "required": False,
            "description": "현재가시작범위가 (각국통화: JPY, USD, HKD, CNY, VND)",
            "examples": ["100", "50.5"]
        },
        "co_en_pricecur": {
            "type": "string",
            "required": False,
            "description": "현재가끝범위가 (각국통화: JPY, USD, HKD, CNY, VND)",
            "examples": ["500", "200.0"]
        },
        "co_yn_rate": {
            "type": "string",
            "required": True,
            "description": "등락율선택조건 (해당조건 사용시: 1, 미사용시: 공백)",
            "examples": ["1", ""]
        },
        "co_st_rate": {
            "type": "string",
            "required": False,
            "description": "등락율시작율 (% 단위)",
            "examples": ["-10", "5.5"]
        },
        "co_en_rate": {
            "type": "string",
            "required": False,
            "description": "등락율끝율 (% 단위)",
            "examples": ["10", "15.0"]
        },
        "co_yn_valx": {
            "type": "string",
            "required": True,
            "description": "시가총액선택조건 (해당조건 사용시: 1, 미사용시: 공백)",
            "examples": ["1", ""]
        },
        "co_st_valx": {
            "type": "string",
            "required": False,
            "description": "시가총액시작액 (천 단위)",
            "examples": ["1000000", "500000"]
        },
        "co_en_valx": {
            "type": "string",
            "required": False,
            "description": "시가총액끝액 (천 단위)",
            "examples": ["10000000", "5000000"]
        },
        "co_yn_shar": {
            "type": "string",
            "required": True,
            "description": "발행주식수선택조건 (해당조건 사용시: 1, 미사용시: 공백)",
            "examples": ["1", ""]
        },
        "co_st_shar": {
            "type": "string",
            "required": False,
            "description": "발행주식시작수 (천 단위)",
            "examples": ["1000", "500"]
        },
        "co_en_shar": {
            "type": "string",
            "required": False,
            "description": "발행주식끝수 (천 단위)",
            "examples": ["10000", "5000"]
        },
        "co_yn_volume": {
            "type": "string",
            "required": True,
            "description": "거래량선택조건 (해당조건 사용시: 1, 미사용시: 공백)",
            "examples": ["1", ""]
        },
        "co_st_volume": {
            "type": "string",
            "required": False,
            "description": "거래량시작량 (주 단위)",
            "examples": ["100000", "50000"]
        },
        "co_en_volume": {
            "type": "string",
            "required": False,
            "description": "거래량끝량 (주 단위)",
            "examples": ["1000000", "500000"]
        },
        "co_yn_amt": {
            "type": "string",
            "required": True,
            "description": "거래대금선택조건 (해당조건 사용시: 1, 미사용시: 공백)",
            "examples": ["1", ""]
        },
        "co_st_amt": {
            "type": "string",
            "required": False,
            "description": "거래대금시작금 (천 단위)",
            "examples": ["1000", "500"]
        },
        "co_en_amt": {
            "type": "string",
            "required": False,
            "description": "거래대금끝금 (천 단위)",
            "examples": ["10000", "5000"]
        },
        "co_yn_eps": {
            "type": "string",
            "required": True,
            "description": "EPS선택조건 (해당조건 사용시: 1, 미사용시: 공백)",
            "examples": ["1", ""]
        },
        "co_st_eps": {
            "type": "string",
            "required": False,
            "description": "EPS시작값",
            "examples": ["1.0", "0.5"]
        },
        "co_en_eps": {
            "type": "string",
            "required": False,
            "description": "EPS끝값",
            "examples": ["10.0", "5.0"]
        },
        "co_yn_per": {
            "type": "string",
            "required": True,
            "description": "PER선택조건 (해당조건 사용시: 1, 미사용시: 공백)",
            "examples": ["1", ""]
        },
        "co_st_per": {
            "type": "string",
            "required": False,
            "description": "PER시작값",
            "examples": ["5", "10"]
        },
        "co_en_per": {
            "type": "string",
            "required": False,
            "description": "PER끝값",
            "examples": ["20", "50"]
        },
        "keyb": {
            "type": "string",
            "required": True,
            "description": "NEXT KEY BUFF (공백 입력)",
            "examples": [""]
        }
    }
)
async def inquire_search(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    co_yn_pricecur: str,  # 현재가선택조건
    co_st_pricecur: str,  # 현재가시작범위가
    co_en_pricecur: str,  # 현재가끝범위가
    co_yn_rate: str,  # 등락율선택조건
    co_st_rate: str,  # 등락율시작율
    co_en_rate: str,  # 등락율끝율
    co_yn_valx: str,  # 시가총액선택조건
    co_st_valx: str,  # 시가총액시작액
    co_en_valx: str,  # 시가총액끝액
    co_yn_shar: str,  # 발행주식수선택조건
    co_st_shar: str,  # 발행주식시작수
    co_en_shar: str,  # 발행주식끝수
    co_yn_volume: str,  # 거래량선택조건
    co_st_volume: str,  # 거래량시작량
    co_en_volume: str,  # 거래량끝량
    co_yn_amt: str,  # 거래대금선택조건
    co_st_amt: str,  # 거래대금시작금
    co_en_amt: str,  # 거래대금끝금
    co_yn_eps: str,  # EPS선택조건
    co_st_eps: str,  # EPS시작
    co_en_eps: str,  # EPS끝
    co_yn_per: str,  # PER선택조건
    co_st_per: str,  # PER시작
    co_en_per: str,  # PER끝
    keyb: str,  # NEXT KEY BUFF
):
    """
    [해외주식] 기본시세
    해외주식조건검색[v1_해외주식-015]
    해외주식조건검색 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        auth (str): "" (Null 값 설정)
        excd (str): NYS : 뉴욕, NAS : 나스닥,  AMS : 아멕스  HKS : 홍콩, SHS : 상해 , SZS : 심천 HSX : 호치민, HNX : 하노이 TSE : 도쿄
        co_yn_pricecur (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_pricecur (str): 단위: 각국통화(JPY, USD, HKD, CNY, VND)
        co_en_pricecur (str): 단위: 각국통화(JPY, USD, HKD, CNY, VND)
        co_yn_rate (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_rate (str): %
        co_en_rate (str): %
        co_yn_valx (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_valx (str): 단위: 천
        co_en_valx (str): 단위: 천
        co_yn_shar (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_shar (str): 단위: 천
        co_en_shar (str): 단위: 천
        co_yn_volume (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_volume (str): 단위: 주
        co_en_volume (str): 단위: 주
        co_yn_amt (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_amt (str): 단위: 천
        co_en_amt (str): 단위: 천
        co_yn_eps (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_eps (str):
        co_en_eps (str):
        co_yn_per (str): 해당조건 사용시(1), 미사용시 필수항목아님
        co_st_per (str):
        co_en_per (str):
        keyb (str): "" 공백 입력

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식조건검색 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        # [필수 파라미터 검증]
        if not excd:
            logger.error("excd is required. (e.g. 'NAS')")
            raise ValueError("excd is required. (e.g. 'NAS')")

        tr_id = "HHDFS76410000"

        api_url = "/uapi/overseas-price/v1/quotations/inquire-search"

        params = {
            "AUTH": auth,
            "EXCD": excd,
            "CO_YN_PRICECUR": co_yn_pricecur,
            "CO_ST_PRICECUR": co_st_pricecur,
            "CO_EN_PRICECUR": co_en_pricecur,
            "CO_YN_RATE": co_yn_rate,
            "CO_ST_RATE": co_st_rate,
            "CO_EN_RATE": co_en_rate,
            "CO_YN_VALX": co_yn_valx,
            "CO_ST_VALX": co_st_valx,
            "CO_EN_VALX": co_en_valx,
            "CO_YN_SHAR": co_yn_shar,
            "CO_ST_SHAR": co_st_shar,
            "CO_EN_SHAR": co_en_shar,
            "CO_YN_VOLUME": co_yn_volume,
            "CO_ST_VOLUME": co_st_volume,
            "CO_EN_VOLUME": co_en_volume,
            "CO_YN_AMT": co_yn_amt,
            "CO_ST_AMT": co_st_amt,
            "CO_EN_AMT": co_en_amt,
            "CO_YN_EPS": co_yn_eps,
            "CO_ST_EPS": co_st_eps,
            "CO_EN_EPS": co_en_eps,
            "CO_YN_PER": co_yn_per,
            "CO_ST_PER": co_st_per,
            "CO_EN_PER": co_en_per,
            "KEYB": keyb,
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get 해외주식조건검색 데이터: {response.text}")

        return response.json()


@mcp.tool(
    name="search-info",
    description="기본시세 > 해외주식 상품기본정보",
    annotations={
        "prdt_type_cd": {
            "type": "string",
            "required": True,
            "description": "상품유형코드",
            "examples": ["512", "513", "515"],
            "enum": ["512:미국 나스닥", "513:미국 뉴욕", "529:미국 아멕스", "515:일본", "501:홍콩", "543:홍콩CNY", "558:홍콩USD", "507:베트남 하노이", "508:베트남 호치민", "551:중국 상해A", "552:중국 심천A"]
        },
        "pdno": {
            "type": "string",
            "required": True,
            "description": "상품번호 (종목코드/티커)",
            "examples": ["AAPL", "MSFT", "TSLA", "GOOGL"]
        }
    }
)
async def search_info(
    prdt_type_cd: str,  # 상품유형코드
    pdno: str,  # 상품번호
):
    """
    [해외주식] 기본시세
    해외주식 상품기본정보[v1_해외주식-034]
    해외주식 상품기본정보 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        prdt_type_cd (str): 512  미국 나스닥 / 513  미국 뉴욕 / 529  미국 아멕스  515  일본 501  홍콩 / 543  홍콩CNY / 558  홍콩USD 507  베트남 하노이 / 508  베트남 호치민 551  중국 상해A / 552  중국 심천A
        pdno (str): 예) AAPL (애플)

    Returns:
        Optional[pd.DataFrame]: 해외주식 상품기본정보 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        # [필수 파라미터 검증]
        if not prdt_type_cd:
            logger.error("prdt_type_cd is required. (e.g. '512')")
            raise ValueError("prdt_type_cd is required. (e.g. '512')")
        if not pdno:
            logger.error("pdno is required. (e.g. 'AAPL')")
            raise ValueError("pdno is required. (e.g. 'AAPL')")

        tr_id = "CTPF1702R"

        api_url = "/uapi/overseas-price/v1/quotations/search-info"

        params = {
            "PRDT_TYPE_CD": prdt_type_cd,
            "PDNO": pdno,
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get 해외주식 상품기본정보: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 기본시세 > 해외주식 기간별시세[v1_해외주식-010]
##############################################################################################

@mcp.tool(
    name="dailyprice",
    description="기본시세 > 해외주식 기간별시세",
    annotations={
        "auth": {
            "type": "string",
            "required": True,
            "description": "사용자권한정보 (빈 문자열로 설정)",
            "examples": [""]
        },
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소코드",
            "examples": ["NAS", "NYS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "symb": {
            "type": "string",
            "required": True,
            "description": "종목코드 (티커 심볼)",
            "examples": ["TSLA", "AAPL", "MSFT"]
        },
        "gubn": {
            "type": "string",
            "required": True,
            "description": "일/주/월구분",
            "examples": ["0", "1", "2"],
            "enum": ["0:일", "1:주", "2:월"]
        },
        "bymd": {
            "type": "string",
            "required": True,
            "description": "조회기준일자 (YYYYMMDD 형식)",
            "examples": ["20230101", "20241201"]
        },
        "modp": {
            "type": "string",
            "required": True,
            "description": "수정주가반영여부",
            "examples": ["0", "1"],
            "enum": ["0:미반영", "1:반영"]
        }
    }
)
async def dailyprice(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
    gubn: str,  # 일/주/월구분
    bymd: str,  # 조회기준일자
    modp: str,  # 수정주가반영여부
):
    """
    [해외주식] 기본시세
    해외주식 기간별시세[v1_해외주식-010]
    해외주식 기간별시세 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        auth (str): 사용자권한정보 (예: "")
        excd (str): 거래소코드 (예: "NAS")
        symb (str): 종목코드 (예: "TSLA")
        gubn (str): 일/주/월구분 (예: "0")
        bymd (str): 조회기준일자(YYYYMMDD) (예: "20230101")
        modp (str): 수정주가반영여부 (예: "0")

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 기간별시세 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        # 필수 파라미터 검증
        if not excd:
            logger.error("excd is required. (e.g. 'NAS')")
            raise ValueError("excd is required. (e.g. 'NAS')")
        if not symb:
            logger.error("symb is required. (e.g. 'TSLA')")
            raise ValueError("symb is required. (e.g. 'TSLA')")
        if not gubn:
            logger.error("gubn is required. (e.g. '0')")
            raise ValueError("gubn is required. (e.g. '0')")
        if not modp:
            logger.error("modp is required. (e.g. '0')")
            raise ValueError("modp is required. (e.g. '0')")

        tr_id = "HHDFS76240000"  # 실전/모의투자 공통 TR ID

        api_url = "/uapi/overseas-price/v1/quotations/dailyprice"

        params = {
            "AUTH": auth,
            "EXCD": excd,
            "SYMB": symb,
            "GUBN": gubn,
            "BYMD": bymd,
            "MODP": modp,
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 기본시세 > 해외주식 업종별시세[해외주식-048]
##############################################################################################
@mcp.tool(
    name="industry-theme",
    description="기본시세 > 해외주식 업종별시세",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "icod": {
            "type": "string",
            "required": True,
            "description": "업종코드",
            "examples": ["001", "002", "003"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "2", "3", "4", "5", "6"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보 (선택사항)",
            "examples": [""]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF (선택사항)",
            "examples": [""]
        }
    }
)
async def industry_theme(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    icod: str,  # [필수] 업종코드
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    auth: str = "",  # 사용자권한정보
    keyb: str = "",  # NEXT KEY BUFF
):
    """
    해외주식 업종별시세 API입니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        icod (str): [필수] 업종코드
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        if excd == "":
            raise ValueError("excd is required (e.g. 'NAS')")

        if icod == "":
            raise ValueError("icod is required")

        if vol_rang == "":
            raise ValueError("vol_rang is required (e.g. '0')")

        tr_id = "HHDFS76370000"

        api_url = "/uapi/overseas-price/v1/quotations/industry-theme"

        params = {
            "EXCD": excd,
            "ICOD": icod,
            "VOL_RANG": vol_rang,
            "AUTH": auth,
            "KEYB": keyb
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 기본시세 > 해외주식 현재가 1호가[해외주식-033]
##############################################################################################
@mcp.tool(
    name="inquire-asking-price",
    description="기본시세 > 해외주식 업종별시세",
    annotations={
        "auth": {
            "type": "string",
            "required": True,
            "description": "사용자권한정보 (빈 문자열로 설정)",
            "examples": [""]
        },
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소코드",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "symb": {
            "type": "string",
            "required": True,
            "description": "종목코드 (티커 심볼)",
            "examples": ["TSLA", "AAPL", "MSFT", "GOOGL"]
        }
    }
)
async def inquire_asking_price(
    auth: str,  # 사용자권한정보
    excd: str,  # 거래소코드
    symb: str,  # 종목코드
):
    """
    [해외주식] 기본시세
    해외주식 현재가 1호가[해외주식-033]
    해외주식 현재가 1호가 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        auth (str): 사용자권한정보
        excd (str): 거래소코드 (예: NYS, NAS, AMS, 등)
        symb (str): 종목코드 (예: TSLA)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 해외주식 현재가 1호가 데이터
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        # [필수 파라미터 검증]
        if not excd:
            logger.error("excd is required. (e.g. 'NAS')")
            raise ValueError("excd is required. (e.g. 'NAS')")
        if not symb:
            logger.error("symb is required. (e.g. 'TSLA')")
            raise ValueError("symb is required. (e.g. 'TSLA')")

        tr_id = "HHDFS76200100"

        api_url = "/uapi/overseas-price/v1/quotations/inquire-asking-price"

        params = {
            "AUTH": auth,
            "EXCD": excd,
            "SYMB": symb,
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 기본시세 > 해외주식 체결추이[해외주식-037]
##############################################################################################
@mcp.tool(
    name="quot-inquire-ccnl",
    description="기본시세 > 해외주식 체결추이",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "tday": {
            "type": "string",
            "required": True,
            "description": "당일전일구분",
            "examples": ["0", "1"],
            "enum": ["0:전일", "1:당일"]
        },
        "symb": {
            "type": "string",
            "required": True,
            "description": "종목코드 (해외종목코드)",
            "examples": ["TSLA", "AAPL", "MSFT", "GOOGL"]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보 (선택사항)",
            "examples": [""]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF (선택사항)",
            "examples": [""]
        }
    }
)
async def quot_inquire_ccnl(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    tday: str,  # [필수] 당일전일구분 (ex. 0:전일, 1:당일)
    symb: str,  # [필수] 종목코드 (ex. 해외종목코드)
    auth: str = "",  # 사용자권한정보
    keyb: str = "",  # NEXT KEY BUFF
):
    """
    해외주식 체결추이 API입니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        tday (str): [필수] 당일전일구분 (ex. 0:전일, 1:당일)
        symb (str): [필수] 종목코드 (ex. 해외종목코드)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF

    Returns:
        pd.DataFrame: 해외주식 체결추이 데이터
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)

        if excd == "":
            raise ValueError("excd is required (e.g. 'NAS')")

        if tday == "":
            raise ValueError("tday is required (e.g. '0' or '1')")

        if symb == "":
            raise ValueError("symb is required (e.g. 'TSLA')")

        tr_id = "HHDFS76200300"

        api_url = "/uapi/overseas-price/v1/quotations/inquire-ccnl"

        params = {
            "EXCD": excd,
            "TDAY": tday,
            "SYMB": symb,
            "AUTH": auth,
            "KEYB": keyb
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()

##############################################################################################
# [해외주식] 기본시세 > 해외주식 종목_지수_환율기간별시세(일_주_월_년)[v1_해외주식-012]
##############################################################################################
@mcp.tool(
    name="inquire-daily-chartprice",
    description="기본시세 > 해외주식 종목_지수_환율기간별시세(일_주_월_년)",
    annotations={
        "fid_cond_mrkt_div_code": {
            "type": "string",
            "required": True,
            "description": "FID 조건 시장 분류 코드",
            "examples": ["N", "X", "I", "S"],
            "enum": ["N:해외지수", "X:환율", "I:국채", "S:금선물"]
        },
        "fid_input_iscd": {
            "type": "string",
            "required": True,
            "description": "FID 입력 종목코드 (해외지수 코드)",
            "examples": [".DJI", ".IXIC", ".SPX", ".NDX"]
        },
        "fid_input_date_1": {
            "type": "string",
            "required": True,
            "description": "FID 입력 날짜1 (시작일자, YYYYMMDD 형식)",
            "examples": ["20240101", "20230401"]
        },
        "fid_input_date_2": {
            "type": "string",
            "required": True,
            "description": "FID 입력 날짜2 (종료일자, YYYYMMDD 형식)",
            "examples": ["20241231", "20230630"]
        },
        "fid_period_div_code": {
            "type": "string",
            "required": True,
            "description": "FID 기간 분류 코드",
            "examples": ["D", "W", "M", "Y"],
            "enum": ["D:일", "W:주", "M:월", "Y:년"]
        }
    }
)
async def inquire_daily_chartprice(
        fid_cond_mrkt_div_code: str,  # FID 조건 시장 분류 코드
        fid_input_iscd: str,  # FID 입력 종목코드
        fid_input_date_1: str,  # FID 입력 날짜1
        fid_input_date_2: str,  # FID 입력 날짜2
        fid_period_div_code: str,  # FID 기간 분류 코드
):
    """
    [해외주식] 기본시세
    해외주식 종목_지수_환율기간별시세(일_주_월_년)[v1_해외주식-012]
    해외주식 종목_지수_환율기간별시세(일_주_월_년) API를 호출하여 DataFrame으로 반환합니다.

    Args:
        fid_cond_mrkt_div_code (str): N: 해외지수, X 환율, I: 국채, S:금선물
        fid_input_iscd (str): 종목코드 ※ 해외주식 마스터 코드 참조  (포럼 > FAQ > 종목정보 다운로드(해외) > 해외지수)  ※ 해당 API로 미국주식 조회 시, 다우30, 나스닥100, S&P500 종목만 조회 가능합니다. 더 많은 미국주식 종목 시세를 이용할 시에는, 해외주식기간별시세 API 사용 부탁드립니다.
        fid_input_date_1 (str): 시작일자(YYYYMMDD)
        fid_input_date_2 (str): 종료일자(YYYYMMDD)
        fid_period_div_code (str): D:일, W:주, M:월, Y:년

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 종목_지수_환율기간별시세(일_주_월_년) 데이터
    """
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        # [필수 파라미터 검증]
        if not fid_cond_mrkt_div_code:
            logger.error("fid_cond_mrkt_div_code is required. (e.g. 'N')")
            raise ValueError("fid_cond_mrkt_div_code is required. (e.g. 'N')")
        if not fid_input_iscd:
            logger.error("fid_input_iscd is required. (e.g. '.DJI')")
            raise ValueError("fid_input_iscd is required. (e.g. '.DJI')")
        if not fid_input_date_1:
            logger.error("fid_input_date_1 is required. (e.g. '20220401')")
            raise ValueError("fid_input_date_1 is required. (e.g. '20220401')")
        if not fid_input_date_2:
            logger.error("fid_input_date_2 is required. (e.g. '20220613')")
            raise ValueError("fid_input_date_2 is required. (e.g. '20220613')")
        if not fid_period_div_code:
            logger.error("fid_period_div_code is required. (e.g. 'D')")
            raise ValueError("fid_period_div_code is required. (e.g. 'D')")

        tr_id = "FHKST03030100"  # 실전투자용 TR ID

        api_url = "/uapi/overseas-price/v1/quotations/inquire-daily-chartprice"

        params = {
            "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_INPUT_DATE_1": fid_input_date_1,
            "FID_INPUT_DATE_2": fid_input_date_2,
            "FID_PERIOD_DIV_CODE": fid_period_div_code,
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 기본시세 > 해외주식 업종별코드조회[해외주식-049]
##############################################################################################
@mcp.tool(
    name="industry-price",
    description="기본시세 > 해외주식 업종별코드조회",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보 (선택사항)",
            "examples": [""]
        }
    }
)
async def industry_price(
    excd: str,  # [필수] 거래소명
    auth: str = "",  # 사용자권한정보
):
    """
    해외주식 업종별코드조회 API입니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        auth (str): 사용자권한정보

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        if excd == "":
            raise ValueError("excd is required (e.g. 'NYS', 'NAS', 'AMS', 'HKS', 'SHS', 'SZS', 'HSX', 'HNX', 'TSE')")

        tr_id = "HHDFS76370100"

        api_url = "/uapi/overseas-price/v1/quotations/industry-price"

        params = {
            "EXCD": excd,
            "AUTH": auth
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래량급증[해외주식-039]
##############################################################################################
@mcp.tool(
    name="volume-surge",
    description="시세분석 > 해외주식 거래량급증",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "mixn": {
            "type": "string",
            "required": True,
            "description": "N분전코드값",
            "examples": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
            "enum": ["0:1분전", "1:2분전", "2:3분전", "3:5분전", "4:10분전", "5:15분전", "6:20분전", "7:30분전", "8:60분전", "9:120분전"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "2", "3", "4", "5", "6"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF (선택사항)",
            "examples": [""]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보 (선택사항)",
            "examples": [""]
        }
    }
)
async def volume_surge(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    mixn: str,  # [필수] N분전코드값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
):
    """
    [해외주식] 시세분석 > 해외주식 거래량급증[해외주식-039]
    해외주식 거래량급증 정보를 조회합니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        mixn (str): [필수] N분전코드값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF
        auth (str): 사용자권한정보

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        if excd == "":
            raise ValueError("excd is required (e.g. 'NYS')")

        if mixn == "":
            raise ValueError("mixn is required (e.g. '0')")

        if vol_rang == "":
            raise ValueError("vol_rang is required (e.g. '0')")

        tr_id = "HHDFS76270000"  # 해외주식 거래량급증

        api_url = "/uapi/overseas-stock/v1/ranking/volume-surge"

        params = {
            "EXCD": excd,  # 거래소명
            "MIXN": mixn,  # N분전코드값
            "VOL_RANG": vol_rang,  # 거래량조건
            "KEYB": keyb,  # NEXT KEY BUFF
            "AUTH": auth  # 사용자권한정보
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 시세분석 > 해외주식 매수체결강도상위[해외주식-040]
##############################################################################################
@mcp.tool(
    name="volume-power",
    description="시세분석 > 해외주식 매수체결강도상위",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "nday": {
            "type": "string",
            "required": True,
            "description": "N일자값",
            "examples": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
            "enum": ["0:당일", "1:2일", "2:3일", "3:5일", "4:10일", "5:20일전", "6:30일", "7:60일", "8:120일", "9:1년"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "2", "3", "4", "5", "6"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보 (선택사항)",
            "examples": [""]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF (선택사항)",
            "examples": [""]
        }
    }
)
async def volume_power(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    nday: str,  # [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    auth: str = "",  # 사용자권한정보
    keyb: str = "",  # NEXT KEY BUFF
):
    """
    [해외주식] 시세분석 > 해외주식 매수체결강도상위[해외주식-040]

    해외주식 매수 체결강도 상위 종목을 조회합니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        if excd == "":
            raise ValueError("excd is required (e.g. 'HKS')")

        if nday == "":
            raise ValueError("nday is required (e.g. '0')")

        if vol_rang == "":
            raise ValueError("vol_rang is required (e.g. '0')")

        tr_id = "HHDFS76280000"

        api_url = "/uapi/overseas-stock/v1/ranking/volume-power"

        params = {
            "EXCD": excd,
            "NDAY": nday,
            "VOL_RANG": vol_rang,
            "AUTH": auth,
            "KEYB": keyb
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 시세분석 > 해외주식 상승률/하락률[해외주식-041]
##############################################################################################
@mcp.tool(
    name="updown-rate",
    description="시세분석 > 해외주식 상승률/하락률",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "nday": {
            "type": "string",
            "required": True,
            "description": "N일자값",
            "examples": ["0", "1", "3"],
            "enum": ["0:당일", "1:2일", "2:3일", "3:5일", "4:10일", "5:20일전", "6:30일", "7:60일", "8:120일", "9:1년"]
        },
        "gubn": {
            "type": "string",
            "required": True,
            "description": "상승률/하락률 구분",
            "examples": ["0", "1"],
            "enum": ["0:하락률", "1:상승률"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "3"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보 (선택사항)",
            "examples": [""]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF (선택사항)",
            "examples": [""]
        }
    }
)
async def updown_rate(
    excd: str,  # [필수] 거래소명
    nday: str,  # [필수] N일자값
    gubn: str,  # [필수] 상승률/하락률 구분
    vol_rang: str,  # [필수] 거래량조건
    auth: str = "",  # 사용자권한정보
    keyb: str = "",  # NEXT KEY BUFF
):
    """
    해외주식 상승률/하락률 순위를 조회합니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
        gubn (str): [필수] 상승률/하락률 구분 (ex. 0:하락률, 1:상승률)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 상승률/하락률 순위 데이터
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        # 필수 파라미터 검증
        if excd == "":
            raise ValueError(
                "excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")

        if nday == "":
            raise ValueError("nday is required (e.g. '0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년')")

        if gubn == "":
            raise ValueError("gubn is required (e.g. '0:하락률, 1:상승률')")

        if vol_rang == "":
            raise ValueError(
                "vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

        tr_id = "HHDFS76290000"

        api_url = "/uapi/overseas-stock/v1/ranking/updown-rate"

        params = {
            "EXCD": excd,
            "NDAY": nday,
            "GUBN": gubn,
            "VOL_RANG": vol_rang,
            "AUTH": auth,
            "KEYB": keyb
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래량순위[해외주식-043]
##############################################################################################
@mcp.tool(
    name="trade-vol",
    description="시세분석 > 해외주식 거래량순위",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "nday": {
            "type": "string",
            "required": True,
            "description": "N분전코드값",
            "examples": ["0", "1", "3"],
            "enum": ["0:당일", "1:2일전", "2:3일전", "3:5일전", "4:10일전", "5:20일전", "6:30일전", "7:60일전", "8:120일전", "9:1년전"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "3"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF (선택사항)",
            "examples": [""]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보 (선택사항)",
            "examples": [""]
        },
        "prc1": {
            "type": "string",
            "required": False,
            "description": "가격 필터 시작 (선택사항)",
            "examples": [""]
        },
        "prc2": {
            "type": "string",
            "required": False,
            "description": "가격 필터 종료 (선택사항)",
            "examples": [""]
        }
    }
)
async def trade_vol(
    excd: str,  # 거래소명
    nday: str,  # N분전코드값
    vol_rang: str,  # 거래량조건
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
    prc1: str = "",  # 가격 필터 시작
    prc2: str = "",  # 가격 필터 종료
):
    """
    [해외주식] 시세분석 > 해외주식 거래량순위[해외주식-043]
    해외주식 거래량순위 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N분전코드값 (ex. 0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF (ex. "")
        auth (str): 사용자권한정보 (ex. "")
        prc1 (str): 가격 필터 시작 (ex. "")
        prc2 (str): 가격 필터 종료 (ex. "")

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 거래량순위 데이터 (output1, output2)
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        # 필수 파라미터 검증
        if excd == "":
            raise ValueError(
                "excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")

        if nday == "":
            raise ValueError(
                "nday is required (e.g. '0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전')")

        if vol_rang == "":
            raise ValueError(
                "vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

        tr_id = "HHDFS76310010"  # 해외주식 거래량순위

        api_url = "/uapi/overseas-stock/v1/ranking/trade-vol"

        params = {
            "EXCD": excd,
            "NDAY": nday,
            "VOL_RANG": vol_rang,
            "KEYB": keyb,
            "AUTH": auth,
            "PRC1": prc1,
            "PRC2": prc2
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래회전율순위[해외주식-046]
##############################################################################################
@mcp.tool(
    name="trade-turnover",
    description="시세분석 > 해외주식 거래회전율순위",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "nday": {
            "type": "string",
            "required": True,
            "description": "N분전코드보값",
            "examples": ["0", "1", "3"],
            "enum": ["0:당일", "1:2일전", "2:3일전", "3:5일전", "4:10일전", "5:20일전", "6:30일전", "7:60일전", "8:120일전", "9:1년전"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "3"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF",
            "examples": [""]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보",
            "examples": [""]
        }
    }
)
async def trade_turnover(
    excd: str,  # 거래소명
    nday: str,  # N분전코드보값
    vol_rang: str,  # 거래량조건
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
):
    """
    [해외주식] 시세분석 > 해외주식 거래회전율순위[해외주식-046]
    해외주식 거래회전율순위 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N분전코드보값 (ex. 0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF
        auth (str): 사용자권한정보

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 해외주식 거래회전율순위 데이터
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        # 필수 파라미터 검증
        if excd == "":
            raise ValueError(
                "excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")

        if nday == "":
            raise ValueError(
                "nday is required (e.g. '0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전')")

        if vol_rang == "":
            raise ValueError(
                "vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

        tr_id = "HHDFS76340000"  # 해외주식 거래회전율순위

        api_url = "/uapi/overseas-stock/v1/ranking/trade-turnover"

        params = {
            "EXCD": excd,  # 거래소명
            "NDAY": nday,  # N분전코드보값
            "VOL_RANG": vol_rang,  # 거래량조건
            "KEYB": keyb,  # NEXT KEY BUFF
            "AUTH": auth  # 사용자권한정보
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래대금순위[해외주식-044]
##############################################################################################
@mcp.tool(
    name="trade-pbmn",
    description="시세분석 > 해외주식 거래대금순위",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "nday": {
            "type": "string",
            "required": True,
            "description": "N일자값",
            "examples": ["0", "1", "3"],
            "enum": ["0:당일", "1:2일", "2:3일", "3:5일", "4:10일", "5:20일전", "6:30일", "7:60일", "8:120일", "9:1년"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "3"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보",
            "examples": [""]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF",
            "examples": [""]
        },
        "prc1": {
            "type": "string",
            "required": False,
            "description": "현재가 필터범위 시작",
            "examples": [""]
        },
        "prc2": {
            "type": "string",
            "required": False,
            "description": "현재가 필터범위 끝",
            "examples": [""]
        }
    }
)
async def trade_pbmn(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    nday: str,  # [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    auth: str = "",  # 사용자권한정보
    keyb: str = "",  # NEXT KEY BUFF
    prc1: str = "",  # 현재가 필터범위 시작
    prc2: str = "",  # 현재가 필터범위 끝
):
    """
    해외주식 거래대금순위 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF
        prc1 (str): 현재가 필터범위 시작
        prc2 (str): 현재가 필터범위 끝

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 거래대금순위 데이터 (output1, output2)
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        if excd == "":
            raise ValueError(
                "excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")

        if nday == "":
            raise ValueError("nday is required (e.g. '0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년')")

        if vol_rang == "":
            raise ValueError(
                "vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

        tr_id = "HHDFS76320010"  # 해외주식 거래대금순위

        api_url = "/uapi/overseas-stock/v1/ranking/trade-pbmn"

        params = {
            "EXCD": excd,  # 거래소명
            "NDAY": nday,  # N일자값
            "VOL_RANG": vol_rang,  # 거래량조건
            "AUTH": auth,  # 사용자권한정보
            "KEYB": keyb,  # NEXT KEY BUFF
            "PRC1": prc1,  # 현재가 필터범위 시작
            "PRC2": prc2,  # 현재가 필터범위 끝
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래증가율순위[해외주식-045]
##############################################################################################
@mcp.tool(
    name="trade-growth",
    description="시세분석 > 해외주식 거래증가율순위",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "nday": {
            "type": "string",
            "required": True,
            "description": "N일자값",
            "examples": ["0", "1", "3"],
            "enum": ["0:당일", "1:2일", "2:3일", "3:5일", "4:10일", "5:20일전", "6:30일", "7:60일", "8:120일", "9:1년"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "3"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보",
            "examples": [""]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF",
            "examples": [""]
        }
    }
)
async def trade_growth(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    nday: str,  # [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    auth: str = "",  # 사용자권한정보
    keyb: str = "",  # NEXT KEY BUFF
):
    """
    [해외주식] 기본시세 > 해외주식 거래증가율순위[해외주식-045]
    해외주식 거래증가율순위 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        nday (str): [필수] N일자값 (ex. 0:당일, 1:2일, 2:3일, 3:5일, 4:10일, 5:20일전, 6:30일, 7:60일, 8:120일, 9:1년)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        auth (str): 사용자권한정보
        keyb (str): NEXT KEY BUFF

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1, output2) 데이터프레임 튜플
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        if excd == "":
            raise ValueError("excd is required (e.g. 'NYS')")

        if nday == "":
            raise ValueError("nday is required (e.g. '0')")

        if vol_rang == "":
            raise ValueError("vol_rang is required (e.g. '0')")

        tr_id = "HHDFS76330000"  # 해외주식 거래증가율순위

        api_url = "/uapi/overseas-stock/v1/ranking/trade-growth"

        params = {
            "EXCD": excd,
            "NDAY": nday,
            "VOL_RANG": vol_rang,
            "AUTH": auth,
            "KEYB": keyb
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 시세분석 > 해외주식 가격급등락[해외주식-038]
##############################################################################################
@mcp.tool(
    name="price-fluct",
    description="시세분석 > 해외주식 가격급등락",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "gubn": {
            "type": "string",
            "required": True,
            "description": "급등/급락구분",
            "examples": ["0", "1"],
            "enum": ["0:급락", "1:급등"]
        },
        "mixn": {
            "type": "string",
            "required": True,
            "description": "N분전코드보값",
            "examples": ["0", "1", "3"],
            "enum": ["0:1분전", "1:2분전", "2:3분전", "3:5분전", "4:10분전", "5:15분전", "6:20분전", "7:30분전", "8:60분전", "9:120분전"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "3"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF",
            "examples": [""]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보",
            "examples": [""]
        }
    }
)
async def price_fluct(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    gubn: str,  # [필수] 급등/급락구분 (ex. 0:급락, 1:급등)
    mixn: str,  # [필수] N분전코드보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
):
    """
    [해외주식] 시세분석 > 해외주식 가격급등락[해외주식-038]
    해외주식 가격급등락 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        gubn (str): [필수] 급등/급락구분 (ex. 0:급락, 1:급등)
        mixn (str): [필수] N분전코드보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF
        auth (str): 사용자권한정보

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 해외주식 가격급등락 데이터 (output1, output2)
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        if excd == "":
            raise ValueError("excd is required (e.g. 'NAS')")

        if gubn == "":
            raise ValueError("gubn is required (e.g. '0' or '1')")

        if mixn == "":
            raise ValueError("mixn is required (e.g. '0')")

        if vol_rang == "":
            raise ValueError("vol_rang is required (e.g. '0')")

        tr_id = "HHDFS76260000"  # 해외주식 가격급등락

        api_url = "/uapi/overseas-stock/v1/ranking/price-fluct"

        params = {
            "EXCD": excd,
            "GUBN": gubn,
            "MIXN": mixn,
            "VOL_RANG": vol_rang,
            "KEYB": keyb,
            "AUTH": auth
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 시세분석 > 해외주식 신고/신저가[해외주식-042]
##############################################################################################
@mcp.tool(
    name="new-highlow",
    description="시세분석 > 해외주식 신고/신저가",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "mixn": {
            "type": "string",
            "required": True,
            "description": "N분전코드보값",
            "examples": ["0", "1", "3"],
            "enum": ["0:1분전", "1:2분전", "2:3분전", "3:5분전", "4:10분전", "5:15분전", "6:20분전", "7:30분전", "8:60분전", "9:120분전"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "3"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "gubn": {
            "type": "string",
            "required": True,
            "description": "신고/신저 구분",
            "examples": ["0", "1"],
            "enum": ["0:신저", "1:신고"]
        },
        "gubn2": {
            "type": "string",
            "required": True,
            "description": "일시돌파/돌파 구분",
            "examples": ["0", "1"],
            "enum": ["0:일시돌파0", "1:돌파유지1"]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF",
            "examples": [""]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보",
            "examples": [""]
        }
    }
)
async def new_highlow(
    excd: str,  # [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
    mixn: str,  # [필수] N분전코드보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
    vol_rang: str,  # [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
    gubn: str,  # [필수] 신고/신저 구분 (ex. 0:신저,1:신고)
    gubn2: str,  # [필수] 일시돌파/돌파 구분 (ex. 0:일시돌파0, 1:돌파유지1)
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
):
    """
    [해외주식] 시세분석 > 해외주식 신고/신저가[해외주식-042]
    해외주식 신고/신저가 정보를 조회하여 DataFrame으로 반환합니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        mixn (str): [필수] N분전코드보값 (ex. 0:1분전, 1:2분전, 2:3분전, 3:5분전, 4:10분전, 5:15분전, 6:20분전, 7:30분전, 8:60분전, 9:120분전)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        gubn (str): [필수] 신고/신저 구분 (ex. 0:신저,1:신고)
        gubn2 (str): [필수] 일시돌파/돌파 구분 (ex. 0:일시돌파0, 1:돌파유지1)
        keyb (str): NEXT KEY BUFF
        auth (str): 사용자권한정보

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (output1 데이터, output2 데이터)
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        if excd == "":
            raise ValueError("excd is required (e.g. 'NYS')")

        if mixn == "":
            raise ValueError("mixn is required (e.g. '0')")

        if vol_rang == "":
            raise ValueError("vol_rang is required (e.g. '0')")

        if gubn == "":
            raise ValueError("gubn is required (e.g. '1')")

        if gubn2 == "":
            raise ValueError("gubn2 is required (e.g. '1')")

        tr_id = "HHDFS76300000"  # 해외주식 신고/신저가

        api_url = "/uapi/overseas-stock/v1/ranking/new-highlow"

        params = {
            "EXCD": excd,
            "MIXN": mixn,
            "VOL_RANG": vol_rang,
            "GUBN": gubn,
            "GUBN2": gubn2,
            "KEYB": keyb,
            "AUTH": auth
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()


##############################################################################################
# [해외주식] 시세분석 > 해외주식 시가총액순위[해외주식-047]
##############################################################################################
@mcp.tool(
    name="market-cap",
    description="시세분석 > 해외주식 시가총액순위",
    annotations={
        "excd": {
            "type": "string",
            "required": True,
            "description": "거래소명",
            "examples": ["NYS", "NAS", "AMS"],
            "enum": ["NYS:뉴욕", "NAS:나스닥", "AMS:아멕스", "HKS:홍콩", "SHS:상해", "SZS:심천", "HSX:호치민", "HNX:하노이", "TSE:도쿄"]
        },
        "vol_rang": {
            "type": "string",
            "required": True,
            "description": "거래량조건",
            "examples": ["0", "1", "3"],
            "enum": ["0:전체", "1:1백주이상", "2:1천주이상", "3:1만주이상", "4:10만주이상", "5:100만주이상", "6:1000만주이상"]
        },
        "keyb": {
            "type": "string",
            "required": False,
            "description": "NEXT KEY BUFF (선택사항)",
            "examples": [""]
        },
        "auth": {
            "type": "string",
            "required": False,
            "description": "사용자권한정보 (선택사항)",
            "examples": [""]
        }
    }
)
async def market_cap(
    excd: str,  # 거래소명
    vol_rang: str,  # 거래량조건
    keyb: str = "",  # NEXT KEY BUFF
    auth: str = "",  # 사용자권한정보
):
    """
    해외주식 시가총액순위 조회 API를 호출하여 DataFrame으로 반환합니다.

    Args:
        excd (str): [필수] 거래소명 (ex. NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄)
        vol_rang (str): [필수] 거래량조건 (ex. 0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상)
        keyb (str): NEXT KEY BUFF (ex. "")
        auth (str): 사용자권한정보 (ex. "")

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 시가총액순위 데이터 (output1, output2)
    """

    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        if excd == "":
            raise ValueError(
                "excd is required (e.g. 'NYS:뉴욕, NAS:나스닥, AMS:아멕스, HKS:홍콩, SHS:상해, SZS:심천, HSX:호치민, HNX:하노이, TSE:도쿄')")

        if vol_rang == "":
            raise ValueError(
                "vol_rang is required (e.g. '0:전체, 1:1백주이상, 2:1천주이상, 3:1만주이상, 4:10만주이상, 5:100만주이상, 6:1000만주이상')")

        tr_id = "HHDFS76350100"  # 해외주식 시가총액순위

        api_url = "/uapi/overseas-stock/v1/ranking/market-cap"

        params = {
            "EXCD": excd,  # 거래소명
            "VOL_RANG": vol_rang,  # 거래량조건
            "KEYB": keyb,  # NEXT KEY BUFF
            "AUTH": auth,  # 사용자권한정보
        }

        response = await client.get(
            f"{TrIdManager.get_domain('buy')}{api_url}",
            headers={
                "content-type": CONTENT_TYPE,
                "authorization": f"{AUTH_TYPE} {token}",
                "appkey": os.environ["KIS_APP_KEY"],
                "appsecret": os.environ["KIS_APP_SECRET"],
                "tr_id": tr_id,
            },
            params=params,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get: {response.text}")

        return response.json()




if __name__ == "__main__":
    logger.info("Starting MCP server...")
    mcp.run()
