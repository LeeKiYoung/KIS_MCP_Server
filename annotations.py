
period_rights_annotations = {
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
        "description": "연속조회검색조건키50 (선택사항)",
        "examples": [""]
    }
}

price_annotations = {
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

brknews_title_annotations = {
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

inquire_ccnl_annotations = {
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

price_detail_annotations = {
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

news_title_annotations = {
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

inquire_time_itemchartprice_annotations = {
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

inquire_time_indexchartprice_annotations = {
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

inquire_search_annotations = {
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

search_info_annotations = {
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

dailyprice_annotations = {
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

industry_theme_annotations = {
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

inquire_asking_price_annotations = {
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

quot_inquire_ccnl_annotations = {
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

inquire_daily_chartprice_annotations = {
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

industry_price_annotations = {
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

volume_surge_annotations = {
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

volume_power_annotations = {
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
        "examples": ["0", "1" ,"2", "3", "4", "5", "6"],
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

updown_rate_annotations = {
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

trade_vol_annotations = {
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

trade_turnover_annotations = {
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

trade_pbmn_annotations = {
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

trade_growth_annotations = {
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

price_fluct_annotations = {
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

new_highlow_annotations = {
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

market_cap_annotations = {
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
