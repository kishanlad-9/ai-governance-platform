# modules/sidebar.py
import streamlit as st
from config.constants import MODULES
from database.db import db_load_all

LOGO_URI = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wgARCADIAMgDASIAAhEBAxEB/8QAHAABAQEBAQEBAQEAAAAAAAAAAAcIBgUJAwIE/8QAGwEBAAIDAQEAAAAAAAAAAAAAAAIFAQMEBgf/2gAMAwEAAhADEAAAAdUgAAAAAAAAAAAAAAAAAch1+Rtsf9t/+f8AeOrXrUcG4AAAAAAAAABwnds4x7onuWzAapAAAAAAAAJbUseboeNpzCWhurXqea0rJHJs5nSuGr12a9Zz2hZU49vHaMxFbuzVr8V28AAAAABzHTs4zddfcTw53okM5tuXQJ4eF7rXnN1r6ZswGuQAAAADxeZxd7J9Cv3xVoDnVVKlYqqVCqpUKqlQqqVCneZkHh/Yvog4Lvfn4OcAABwOLfoh5PsWQ9BUv9eZL1QVqXqgMs1blrzc2MvVBTV0vVAYr4T6E+f7BzXdngQc4AAAAAACDXmDXm9swoqw8v1JZCOAAAAAAAAAM9Uqa0j19/8A1xXZ8VqhKLHHLF6C1s4+a+OAAAAAAAAAg15g15vbMKKs8j1ycghEAAAAAAABy3UwS07eP0Jl2oetvryPn3lAAAAAAAAAAHg+8nKH1P3Xd0hXcgAAAAAAAAAAAAAAAAAH/8QAJRAAAAYBAwQDAQAAAAAAAAAAAAIDBAUGFwEHQBMWMDYQFVAg/9oACAEBAAEFAv3bNZmtXY5ifdetWVrZ2PG3eMp3ANoDKfe8a21NC1MsSzPXqdUb1Vj+XeLppVkC7l2Aq9OtidqYC7XElVaZLsHXpVwJamYudtTqrE25dg1XpFzLaW/m3ZQUTso2dQU1fjd5BQs8Nn0FTTY3hQU0kxtIgqex+awV1nZGZdmydeHhmsCxE7AtLEyw2TrwcE0rzETUK0n2JtmydeArzOuMvxXc3HsFEV03KfjXXTbJtJpg/U8N4m1IKBOcyh6fZz12SyZCDJkIMmQgyZCDJkIMmQgyZCDJkIMmQgyZCDJkILfZlLFJEOZI9Jm1J2B8F3g1J6CUTMiem1c9ikcbQYxtBjG0GMbQYxtBjSrR/deNoMY2gxjaDGNoMY2gxcawpXZJNI6ylKhDwMD4XUQxfHSSIgT+S++/yqiRdNrEsWJ+CX33kF99+dZVlopxHLtNjdO9Ysd6xYs9tI9bCiy6h1OG6aJvrp2RFjsiLFnqZGLcUSJUKrwy++/OsQx1U4hffePPzycG30mVtJeBnUpxtxr+U/2o2/Kf7PjTEMhNNser9SIh0IZt+7//xAAkEQABAgUDBQEAAAAAAAAAAAABAhEAAwQSMBATMRRAQUNyYf/aAAgBAwEBPwHslFhCVF8oSBiUWEJJeFFhCSXhRYQkl8IAGgAGgAHcViEostHgZa71/I0KSOcdR07I3ndhxFP0e6LXf9ivs2DdjrvX8jQqJ5xUcpM6cEq4ivp0GTd5GRKig3JibVzpwtWe0//EADARAAECBAQEAwgDAAAAAAAAAAIBAwAEBRESFTFTBhMwkRAUQSAhMkBDUXFyYYHR/9oACAECAQE/AfkmxxlZYdaFBunURVRbpBOkaWXpNChFZYebHDeGhQissOtjhvDQoRWWHWxw36CLbSCMi1hFtBOEWsaQThF7l9ui8P5m2r7h4R0iocOzco9gZFTH7okZRUNgu0ZRUNgu0ZRUNgu0ZRUNgu0ZRUNgu0S3CCuMITzmE19LaRMMHKvEy5qK29mi8QLTG1YcDEOsVDiGbm3sbRKA/ZFjNqhvl3WM2qG+XdYqVSnW+VgeJLinqsZtUN8u6xm1Q3y7rEtxeTbCA83iNPW+v5iYfOZdJ5zUlv0ar9H9E8FEh1Tpznk8LXmcV8KaRJ5Zzxw4r/za0Vbl+ULmf1+enVfo/ongRkXxL0qbLhNTKNuaRVpNopZXNFHT/OoBk0SGC2VImKhMTQ4HC93yn//EAD0QAAIBAQQFCAgEBgMAAAAAAAECAwAEERIzEyExUZMQFDJAYXGxwSAiMEFSg5GSBVBTgRU0Q6Hh8DXR8f/aAAgBAQAGPwL8909ovd21RxLtc1fzCz6H4cRxfX/Fc4s96suqSJtqHq9mDZQs4w/cb+S1gZRs/rd+IXefV1jdtDaI9cUwF93Z3Vg0llwfqYz/ANUYo20s8muWYi7F/j8sjjhQS22UXqrbFG81pOeKw/TMS4fCmkw6K0xapYx4js5EwIJrZNlodg7TWk54t36eiXD4U+JBDbIcxBs7xyKwQS2qXVFGdneeytJzxQP0xEuHwp0lQRW2HpquxhvHt0kbLkgXAe6+/wD3t5PxCb+iIwh77/8A3kssxyns+FT2gm/xHJbJhkrBhY9pYXeB5LBN/RMJQd4OvxHJLKuWkBxnvIuH+7vb83tanVrSRekh7K9b8UYw7hD631vpbLZI8EY19rHeeQ2a1peu1WXpKd4r/lG0O7Q+t40LLY0wptZj0mO88jWW2JjjOsEbVO8Vq/FG0O4w+t9b65vZE263duk57fybR2m2wQP8LyAGhJFIssZ2MhvB9oZJpFijG1nNwrBZrbBO/wAKSAn2TywnDPIwiRvhv9/9qLMSzHWSffSl3bmUmqVPOsybh1mTcOsybh1mTcOsybh1mTcOsybh1mTcOsybh1mTcOsybh07K7czQ3Qx+ffQdGKuusMNoqOaY3zxsYnbeR7/AKEexeGHXPGwlRd5Hu/vTI6lHXUVYXEUukRuYx65X2ftWRJxTWRJxTWRJxTWRJxTWRJxTXMdG3N9JhuxndWRJxTWRJxTWRJxTWRJxTWRJxTT4EbmUhvifypUjUu7G4KovJqOCbVO5Msg3E+7w9ljtFjgnf4pIwxoJGixoNiqLgPS+d5ekUkRZEO1WF4NY7NY4IG+KOMKepfO8us/O8vQ0ZtcAf4dIL+qyTym6NJbzd3Vmv8AYazX+w0sFhkYK2Y1137cj2GRiyBcUd/u7OqSQS643luN3dXQk++uhJ99LPYUYouYt9/78j26RSqYcMd/v7eqfO8vQ0hscBffox1X53l1gMRpJn6CV/EcKabFiw+6i6jRyp003dXhJ6Gi1fU8loI6Gi1994u8+r6KbURrVxtWv5uPR78Jv+laKHWTrZztY/n3/8QAKhAAAQIDBwQCAwEAAAAAAAAAAQARITFREEFhccHw8UCBkaEgMFDR4bH/2gAIAQEAAT8h/Ohjwk9/IBeUKhMK9Ui1bcQg3HpyXZyG5z5UB6sFd3ppZq/fp3cZMwMyF5MPCFQNE2USMIMEQAkALgj5P4w+T2CfGjADA0TwObydSDvaa5PB5wHliGPg52AV6ncITw8L0KoXual726gNAD4gZYZYwusK8ckGgnhHGb90xjm8jUve0N5wM1K2MxdCv3hrOAEQB5jYDUEEy4m4eh5WDxLS5QNsnYEE4OPAeLI9QXRuBp9LAKpA+4/QH+862e4tUFpJDufEuGUk92U+dxJe+EvNhaz701UIRk5dwUeHu3ZEkgLi9UXmx0aHBroS4otwzpUspJ7snFgCc3qC0l+G4AbgSpVqVyhH2SfGuLMlHwl/WAP1Y9o2ASfAu7Ii93NyVSUbAIziMBFR/i5SuUrlK5SuUrlK5SuUrlK5SuUoTA+EA1Yq/iPIR1YlQVlPIKEd3cfSA3DihB7gXdkSvEUChCYpEmQNBNT6C2zqts6rbOq2zqts6oy/KaNFNbZ1W2dVtnVbZ1W2dUACr4wBWaj/ACKjJeIFAEGRjGk9APqCIel5cIQbwsCyAHym5vlhbjBZgFHRHn5cA6Kbm6nNzfDEZLOisnTv0hmxgoObe2zg64wyLg1sfrJieExyRft0gUySCTFeSrkqdeY8RgXZK2F2M2jRmOSDd+km5vhisF3uvWSAYMIDpJubqMT2A6z1JwCyCGN1mm6fUoA5fARgenAdniKXiaWEOTW0/wATp0Yh97n6wUnNbhqmnEjajt+e/9oADAMBAAIAAwAAABDzzzzzzzzzzzzzzzzzyybzzzzzzzzzzz97zzzzzzzzyle/S5Lzzzzzzy122293zzzzzyTDLLLLJjbzzzxiYwy4ww5zzzzzzzzz/wAz8888888888jST8888888888/8s8888888885k88888888888vf8APPPPPPPPPPPPPPPPPPP/xAAkEQACAQIGAQUAAAAAAAAAAAABEQAhMBAxQEFRcWGBkbHh8P/aAAgBAwEBPxDREYIQhuEAhGEGLRGCUwwjBKI4RglEdgh0MyQQh0MqgEIdDCjA1FAgZitzzdzYBGhDt9OKhL1g80UoT2+vM+D97L9lbzYBG5KtcqY9raEyoIXXFwdIiMjBNkcID3Wk/8QAKBEBAAEDAwMCBwEAAAAAAAAAAREAITFBUWEw0fDB8RAgQHGBobGR/9oACAECAQE/EPojHBSUYTqGkvU0LdIngoDBCUDwUVghKB4KkwQnQRTlQsOaRSZoOHahVJQctvndyFhBKplvYDGss4i8kKJEf4hMJ+yHg989q989q989q989q989qQuCYSJaN5XeIhtfNZxotrbcOT5ZWCwhhFyXsjHEM5moN0QIPypEr9rEHL5N615N60xeCYKVm7fNeTeteTetIxBGAhrYo7xMu1M9eLa+3Bp0c/Ln4RsxOJI6f2U9sR+dZmju5bWaTH65itHf1sj14nTp5+XPwgRGMSz0t8QpvGnfiiwQQXA+DnqZ6AEoLKGgBP3jP8+k/8QAJhABAAECBQQDAQEBAAAAAAAAAREAITFBUWHwEEBxwSAwgVCRsf/aAAgBAQABPxD+7CK8YASwtpQrhJZUG4Uvx8Jddv8A4pEoN8mkgxYEo2QcEQ7Z9vOtmfhdjofeMWmk7xBs9uaxJYEC9GICREI2RXMdv/bZ+Mo/c6lUvYASebiBKyi3t/LWr5rEbMRDICS3CxP3Qph4Am4HenM64qCub4INxBmBVCUC0QxCRQoARU3IUBM2K+ku/wClJLQyM5fXmBSqIVkWkeK+SBNL5IXQBLhHYqiHkUd2W9Nqy1noDShgRZNzCPuafmPKIuopGxz6NTuJEXzVPChr0SXRuFY9wZ8egBaSY1VvJ/HXo2Plhotl8uNugGbbnGjqqBu0+8OUUw4QoEhIFCoJJBCZHNYtwg+TxUx5suuNXYL4AAAAFWL6si0IbDCiIiWRq5Uvw/6CUFQJLNgMckALAAAAdFKnR7xIdhl1EURFFC5zADYBPg8UeJ0pGxEAsWAAvBdn+KTRYYfHBZgbpFCGGTi1Uj+P2DViTT3QH60WVFs+YpMTcI+qJOwkokGpF0S2px81rjKi6rm1euc+JI1fhkuyMyOH+64f7rh/uuH+64f7rh/uuH+64f7rh/uuH+64f7pKApkjZ1LLLcEyUbrLMlkBcRzKtGsaIiBqg+WGH0k5RZC8Q4IpliRjT0msAWFFxHJp5gOrCTm7RMXkdJ+L58+fPm621m4Xzj8nz58+fLAI+XCXX8l2UGZgjomybAC6uhRaHQCCBIsozFpGJPqDdoBgMCUxtURAjU0AAePlzOv5BHyHtoBH9oDPomBxITG3Zczr7nmdfwdkspQ0Yk7UACIjcTPtGgXFIYWC7dK5n6rmfqkyIltaKbwysMYDBTo39k6RA3UAGBLXtE01DYJWTC4dVVV+6LAdHOFzRI4C9DriUxgkaCBwZadpzOvrjTdslaWo4nfGgIACACAO05nX3E9+j4WJeUxuqBmkNvLnVwGBG9IRuCozKziYYmRMpe2DmTuhF83lsnQKpZ9RA7xB4e3DEwhZpCk4q0rGDBBC76Vtdbonasf2ou0iWMAwBY3VX+7/AP/Z"


def render_sidebar():
    with st.sidebar:

        # ── Logo + brand ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="padding:1.2rem 0.5rem 1rem; text-align:center; border-bottom:1px solid #1a1929; margin-bottom:1rem;">
          <img src="{LOGO_URI}"
               style="width:64px;height:64px;object-fit:contain;
                      border-radius:12px;background:#ffffff;padding:6px;
                      box-shadow:0 2px 8px rgba(108,99,255,0.3);margin-bottom:8px;display:block;margin-left:auto;margin-right:auto;">
          <div style="font-size:0.92rem;font-weight:800;color:#ffffff;letter-spacing:0.02em;">AI Governance</div>
          <div style="font-size:0.62rem;color:#3a3a55;margin-top:2px;letter-spacing:0.08em;">TEKFRAMEWORKS PLATFORM</div>
        </div>""", unsafe_allow_html=True)

        # ── API Key ───────────────────────────────────────────────────────────
        st.markdown('<div style="font-size:0.68rem;color:#3a3a55;font-weight:700;letter-spacing:0.1em;margin-bottom:5px;">API KEY</div>',
                    unsafe_allow_html=True)
        stored = st.session_state.get("api_key_input", "")
        key_in = st.text_input("API Key", value=stored, type="password",
                               placeholder="Paste any LLM API key…",
                               label_visibility="collapsed")
        if key_in:
            st.session_state["api_key_input"] = key_in
            from utils.helpers import detect_provider, resolve_model
            provider = detect_provider(key_in)
            icons = {"gemini": "♊", "openai": "⬡", "anthropic": "✦", "groq": "⚡", "unknown": "?"}
            icon  = icons.get(provider, "?")
            if provider != "unknown":
                _, model = resolve_model(key_in)
                st.markdown(
                    f'<div style="font-size:0.7rem;color:#1D9E75;margin-top:-4px;padding-left:2px;">' +
                    f'✓ {icon} {provider.title()} · {model}</div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div style="font-size:0.68rem;color:#E24B4A;margin-top:-4px;padding-left:2px;line-height:1.4;">' +
                    '⚠ Unknown key format<br>' +
                    '<span style="color:#555;">AIza=Gemini · sk-=OpenAI<br>sk-ant-=Anthropic · gsk_=Groq</span></div>',
                    unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:0.7rem;color:#E24B4A;margin-top:-4px;padding-left:2px;">● API key required</div>',
                        unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Module navigation ─────────────────────────────────────────────────
        st.markdown('<div style="font-size:0.68rem;color:#3a3a55;font-weight:700;letter-spacing:0.1em;margin-bottom:6px;">MODULES</div>',
                    unsafe_allow_html=True)

        for mid, num, mlabel, mstatus in MODULES:
            is_active = st.session_state.active_module == mid
            is_locked = mstatus == "Locked"
            css  = "mod-btn-active" if is_active else ("mod-btn-locked" if is_locked else "mod-btn-inactive")
            icon = "🔒 " if is_locked else ""
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            if st.button(f"{icon}{num}  {mlabel}", key=f"mod_{mid}",
                         use_container_width=True, disabled=is_locked):
                st.session_state.active_module = mid
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # ── New Problem button pinned to bottom ───────────────────────────────
        st.markdown("<div style='position:absolute;bottom:1.2rem;left:1rem;right:1rem;'>",
                    unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1a1929;margin-bottom:10px;'>", unsafe_allow_html=True)
        if st.button("＋  New Problem", use_container_width=True, key="new_prob"):
            for k in ["messages", "extracted", "current_status", "submission_id", "m1_step"]:
                st.session_state.pop(k, None)
            st.session_state.submitted_records = db_load_all()
            st.session_state.active_module = "m1"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
