import requests
import telebot
import threading
import logging
from flask import Flask, request
import os
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

bot = telebot.TeleBot("5838783352:AAGBJSOdnVlOdvKhbtS8fVnSaz4nhDOzDqU", threaded=False)

user_states = {}

def instagram_login(chat_id, sessid):
    try:
        response = requests.get(
            "https://i.instagram.com/api/v1/accounts/current_user/?edit=true",
            headers={
                "Host": "i.instagram.com",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US",
                "User-Agent": "Instagram 123.1.0.26.114 (iPhone 12 ProMax)",
                "X-IG-Capabilities": "3brTvw==",
                "X-IG-Connection-Type": "WIFI",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Connection": "keep-alive"
            },
            cookies={"sessionid": sessid}
        )
        if "user" in response.text:
            bot.send_message(chat_id, "✅ تم تسجيل الدخول بنجاح.\nأرسل اسم المستخدم المستهدف:")
            user_states[chat_id]['step'] = 'ask_target'
        else:
            bot.send_message(chat_id, "❌ SessionID غير صالح أو انتهت صلاحيته.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ: {str(e)}")

def swap_username(chat_id, sessid, username):
    try:
        burp0_url = "https://i.instagram.com:443/api/v1/bloks/apps/com.bloks.www.bloks.caa.reg.username.async/"
        burp0_headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Bloks-Version-Id": "a9f3a2e44e36b8ec4c852e8fcc580c4da91838901b581613b344185285c021cd",
            "X-Ig-Nav-Chain": "SelfFragment:self_profile:5:main_profile:1755705348.308::,ProfileMediaTabFragment:self_profile:6:button:1755705348.516::,SettingsScreenFragment:main_settings_screen:25:button:1755706916.491::,com.bloks.www.caa.login.aymh_single_profile_screen_entry:com.bloks.www.caa.login.aymh_single_profile_screen_entry:26:button:1755706925.871::,IgCdsScreenNavigationLoggerModule:com.bloks.www.caa.login.aymh_password_entry:27:button:1755706933.848::,IgCdsScreenNavigationLoggerModule:com.bloks.www.caa.login.aymh_single_profile_screen_entry:28:button:1755706937.124::,IgCdsScreenNavigationLoggerModule:com.bloks.www.bloks.caa.reg.contactpoint_phone:29:button:1755706939.337::,IgCdsScreenNavigationLoggerModule:com.bloks.www.bloks.caa.reg.contactpoint_email:30:button:1755706942.800::",
            "X-Ig-Timezone-Offset": "10800",
            "X-Ig-Www-Claim": "0",
            "X-Mid": "missing",
            "User-Agent": "Instagram 381.2.0.53.84 Android (28/9; 320dpi; 900x1600; OPPO; PJH110; marlin; qcom; en_US; 737027401)",
        }
        burp0_data = {
            "params": "{\"client_input_params\":{\"validation_text\":\""
            + username +
            "\",\"family_device_id\":\"97b3895a-649d-40f8-a516-e63aae231f80\",\"device_id\":\"android-d71ab773d39dfdbd\",\"lois_settings\":{\"lois_token\":\"\"},\"qe_device_id\":\"3b67cd48-7663-488d-8509-4caf099a935e\"},\"server_params\":{\"event_request_id\":\"88733f3c-754f-492a-9e50-f84ec57426a9\",\"is_from_logged_out\":0,\"text_input_id\":124411143600025,\"layered_homepage_experiment_group\":null,\"device_id\":\"android-d71ab773d39dfdbd\",\"reg_context\":\"AViBWASoKF707ayz5PFyhU35TqoXluBvIWKQKvd5SWRqbsqjedOsIVx1zxATf98p6R4_Plea3DZtP8nb0k-CEZKp9OXZVtmFOQHd7GfkcyEjY5m9cg0AVjWnprDYUPFuqTjyjjyed1n7glsvRmUUWf-RrjJFiEasQ9YGEyfITArsS__flY57kEzyZL8EPirhXk3DLTqn2KV4Le6YfIRYKMVTspbcJRCBDbMQPnORZKLbv0g7r7hp6ymqXWqXNmcMl8waRCdZSGO5rOd20FHpnX4GmAyxoNE6D8fiYRHA_IgBeQkSeF932h6-7O9F9jWIzrq40yJPjsdteK9-6qi-nXpFGMcMkGHrgkdkzYndu4Tav8wjxT3y3ZMuGKlvKsblB7gxA3X1RWxcmHrrULasy1E7Y4QPrByBHARy6VCxd3xgBa3vHTC2_ib8s58u4hC3p0yatwZ6Z7aPCiUV9Zjw7Y1WWUBVOHSJZDlhDB83IJgE9sUJO5XB-w8HQsBvfaqUMdB4GsrJuvliSOY6dg_bLo34xS8jxt0dxVSeFoIy8D_mjh41PPsD1GNOHkFFoDLB_J17CbbP1rmFlUaR0cCwtubQKEvxWElGjDHWZsNGIInyRguexq7iR5PcZF2tGIE3RnLru2kQCQjjeEZfRFlIQzl_0r72uOaSAH1i5uweQc1yEZhbsrIWCkvP8jVBCLXfuTj5y14Fq7eYczVUMzjCwGG5UvCxS5uyM9uJaSPPutiD6tiYGp-vCzTDQzD6bIA0CbGu6sU9AEjk80S7Cgq88IqmfycSRhV6Usr7sMAq-uqJzX3VM4K_42eurrxP2hKfe55JGO5EHsgKiO7g1roryeZ3GajpnQ53kVqnxwc_4X0YU19oScpd8y5-pLj_W5Decla7DjELUO92cuuxlzUdTmXfAH5fNvw7axJh0GrQLa-_bJgvP2VtsTDXkITt-Yt3VigHTJ_t51Texd35wKQLmoRy6pjxnZyuuTD0ScovYOGWLx_ZYIZjjPEn3SoY3CVuZHDSbl8skY1L6sACu1GZD-6Bks_I2NQfkGB8Iwls8GonZnT8wa_fv60QgR7v43w_0gLJ2_zUVZ3xosP0OaQOhWGjhIKjPklq5jsMDSh5789i3dcUlb6RyiUwbufLa7Kg87do-CxL9Ai4ryM1Cxd_JJH3MJg9_wOrqvavL7JE3U_yBNZy8OUxcgRHFXP0AU9J7Jx3YQ83KkXgbPPvHjezqVI8ewRhNE2PcBPSrYngo1oR6xiaUbviSLmmg8mPqSXFXCWeruaV7FEuE4mmYWCIQ635gIqABB9ONR1KKERBktqU_TQPWGzku-eRO-KAcRLqJx5O5mPciHOmwrw9mYuloLxqhifUpfKHSum4NaPNw8NoHEXUTrzoHH__uFxft3lEs-jQMQaphnrZKN5kWGRI-1nU0X5CJLwOi0yFBbLfxEa4jnleACUf-Hhj9EwpgsBbZEIhVgFu1VfhQ3tYxAJTPDDyMiBoCtJWRwLF72JCX6o0skdmBpiyrkwRyIA5SZJJ7n48Ujw5cjYbaWxd4uZucbfx1A0moW-Gz-gHkTpFedzgrN72LU2SbfqtU0cZBv8_528uiJADI-NlVw9vK-FiIwIl6ohNoBmRgfP-0UaWp2IJbk6QfJRe8_iXPaH2PGzsvD46k4GP53-IxvNSijr5U5Qr_5eyMwL_JagTjZdCwWNV37KEr1jZtfmDp8zOHzaDBIAWMvtWrHDHlcVIQkD1U3mPfGkzhWVkkt72xy_fkTY4UkOD91-5J_I30Pd-HksyABfotG9Wgn8AKjfpy88ONv42IG1eaZ0BOaEB4LQfRzUHgSNC8NUt6yCj2d7y8bCtepAVFVFuBji5NPQqURGiEd81B7x4RdmtVdQ8GcLVZxsqT1SR-OPiFV19J9F9Dzskn4ZmrpzrnK2S_FrtQbO6dGCUQVxMz-aYVIYOS5avG54Ivlp3DNCBzZ7wGZLTxoX_zxHnakR0hmPIivFkui0udihzfP9Hmj4vyuI_oy5OiBkhibrupj2Gtc9lkdw_n6SmoTtGAAsHibFW7ESAx0BtUYoySi5tcZ_ksEmlyUOk4S51ewyrVy-MGplo-r1_uhUTJfs880nf-9skfzy6VEthmHMz-r88UF1d_RB06uD7t3luEDJpYWQe2XkoE2ehEnY1S3jVBLy2Cs9pbf03XbSGAxoKvXDosrP7UZnUQyehxzrydWRaPmRHEdb0Y9550cpd-oPVTyI3QxlAxFmxCr_SK6pkONhidGdueQ98durnRIrrycu6qA-yYR1zDWOP-37yJapIhaodGHAx4_HXBYp1H8URzOuroIb_xiOZXRtgLcmV7j02SnejVHF5rEnMXkVcQqCWo45EAEAfBjHa9fQwMqGkVWabAYagtSRz79WsD6Pdd8hNs-8dMOiguGHkUP7xQJsoo8zagZ4e-T1-qALi5GUO7T_loWZrpeegnfSnwhSzn6HlRBsKnZCmmPDgorCCf-f78CxnMeIRp17_J4JyY061J_VdgCNO_CZvfRHgYYP7zKhx_Le6ZFtJry2OuIfPn6cz27g4dVHR1R_lGFMi237ChEdfN_o0FBiHlkIXNtd6Znf-mvBwFWtm2KAkxaymnbo0FrQj3Nu3NLDc-5KUTUGKFlKQiEvQl3Tv5YjncH_CqIyIpXr4cDz9mGRKbUk8YhXElPT-Qu-VFts9Mf0Is0B4teJMn0mWKITgQzcbPOjdIxIokRWAla_2A-nhq7lzjIfSse48V6vzufej5AX4k7JlfSb_XPVzq7jbBTmBg9bU83Ob6RBka9mZrDLAwqWGstKq8Tk0JMcJ0D-_Xveay7Sp0-6w3jjHoW_o7H5jgPxFq4Uyu7FIpXF7MUc5N8vWdAe3a5Kmt-Ab-mS8-_Kg4PhUFGEEJataOQ4BcoIY8G8BEXFr9s0iFgn8X05xBxCMIFqaDd2tFYT-GSlMgdEVByC7ynHd1tf-R29UyqRu_84UPXvJMJE-GlJUEPX0wsGXmztZ7Fa8ZOBMfS1xeCaEcGXbxVUBtTrIshouluHGALSqNqE5uEPlPkWnTPmzZ17CYXigU2fNIMOxqLNOlpQdHMxxRN8XXkQ_hXVh-DGV35epFgeH79g5EThmDOvrBVeRbxkypIGlOazAe_Fw9tZtiGNN2sCQ9-pV8CJllARNdFFTbnnapKRzNXk4ydztz49MbsjJJ7MFmPXTnaudIX_bUBtbq8pmKz0P8OCRsZ-QspYKWxM-yF8sI9oe7LFRRsX2FSLbnCyIK5x278Qx6KuMd5BoZQstkxCbW4GSGYc0lBKBk8Z5XvJB-ppq_nTZgmuEfcCz5HDgc_h5olzIHBaDJ2ucEOXg3RK-yh49olTC41eQoBnxhkmUoBNUlv48enPH8FkxfyJ5iGgo6KAL6vCkqLN6KAO_wgQeo5-w7f7aN1AgIcxeYa3EuU__AQariAF9A-WXKOxvcx3fm99s8Ozilf8rQni4-qhAy8pXSMdn93PmSZMtuTD9sr7xzkmVlvwz-i7h69iUXMhk_9UWKfb8I2h6RFz0LKBfqq6XKEIDuuFk1ALS0ViADe-7B3ycyRvQAgEDzp2amfxG7c3jhKzHxKAzi5JACEv_b8H_Q0HdheqbKZkRcDNDjk1TaDtRZnQsGwpOqVjH3a2WcpWZxKPUq-xYk24ud7K23CuGbILXEdJnX-C7ih5cQZlMYcCXlI1Lk3-KHk02OrIP9DFhodegJLA8kWieExstqRc2JpEQjZNNr6bpW0k5KHF_3vAOkzOkUdYqR2qmMAjsqYj5XWCshYJazAQ8BX9XLU2WX9NU9EIFu4ry0-TrfAlTcivhHxY60xxkKtsG4qBPL2Yp8EbbQbV0C5ssZLolgarOn_4JesLkxcjoKII5szYNgj-2rm2X-IbWcknbMH4PCEIoq21Xg-Gt6RnOdisCPai3Cxw799kIWhsXN5vR-Yxsri4lYuV61IkAL3s86nHDfAIW8Y-B4bMoaTtigh6uAJGggNnUyGjvAShW9Y7geuZ9DHh24AEk5FBGnG5MfvWe_4FZ5aAoCX9ke83pJ6exgMGZc5HSXzl7LifMZ2S6wX2ehR531yHlV5aR7XWgeJ_fwLqUmg8oB6tbebj0k_hODU-JkMPglDcaPbDt8jny9eLQxhZ1QbLCKDtcvGQeIDY7OFgCOisRTVHYFG9e1NT4k8cjObQ1PTyPrmrJg_k6-w8xdtoZEvxqeHux6XE3T035zWQZAzNbbBGvTs6AbJ15VeIyroVy7SF1AIZHsKAu-xeBNSHxU2ZvHa4jv_GWO4L5nX9g04bb_0bS_ziBXHcPX17tFtv1oJ7QFurIAvz6veT83-sznixwzk5s_tCX_14BuoUveXekCdmuBOUt7ZGwZbZgdmaJshvC2JG4Qf3xVfwEyGnwh1t7lpRZ9HCrrnEDrzwQ7pRBGgBao3hjHbgIlp6FuyYvYayCik55ZSg6lIymOAPEf0l1iLAQKF8ONgzxENoBUigoXf6kYR_nnzlX6Sn2bP_64XCO_6xi5VRcTcfXLrvzwxyYv8dqcVh0qROksOLRr9J0nQPwNkPkzcKL587CVXKOHtNtI821aOrMKuNRlN5LSZ5bfMICagPSn9pNaqlkRK8EzPmMsv_K1aVf2MAOQdZcs0OhCDVGLvOOUZA5mq9W_Q1h1g2Bk_wLCXeqFJi_DIGr-cqhvKH0cZM0tKiVMiewouRjTP7BWAg4Hvt3FLCnBbY5Fc3d0vThhk2XkEKHCV5A2lR1F_Q8gDZZpNz02mfDu6rO_5rh78824f2-qg6iiSCqp5_rvGJS9FrlQT9d28eMbulaM0JTySXrP6QgWqhjrl0nCA1saTnTdvJcSRd-yCBrw4z_VTX5J-szG00BaeaoK187cfS_nEWCWbMqZ8ryI2uka0lFdYnUnaSldjQ7T-cUMIyxfi1fuMC7UTp2oA2I3dXKsPrzOQjU6nLov_YaCiC955ZCKAMYDnNF2q9wyf5SGHr7FNFyvfnEv4PucBb5Xr8joSNJF4EzRKxeGCPgsTAUmLr-iNH_5Ve8ZzTvQcsUGRKOl3B7DAhWy_0S2XxhZ00f9-9oAvszNaEzz2rPCu0z9bqtaoDzUYSvcemuMiuBO9p7vJmOLWycuSvbTjDDpfwFo7hWr7j0vyXWHyD3xuGBcNkkfcS7sOJURhWlLyaBQbfrA_-Yd1aoVt9tDe0CUnabQ2PFLOtre53_uMGzhSbMcnX1tVuEWphcg0pP09s3sXAeCjkfkTcyzk7Z9Izy6_BX-syd08RM2gpXSUUJu7Bin0IMyoCUiFwgCt83gaUqDTnTFNbiFymOEyCBVTwbNEIG879OipegFOImg0x0-DRPo8oWuZ4U1aQ7fM1iw_9Q9KmLiHq1jNWKAwfTcC1EZ2iTRQ5vvwPwIKYywvCkKYzWIylneFyWV6uhGlNwBcZq01Lh2qvvmQUDf8Tn2jCxckjJVBz83pbvc5OqExGKDVFicpSAOgduvgI1LpkVVUlA6nX-XVhAzgQwZm_x6bvpzLo_kvxajUlYhTh9UbML9IATA6pcmcT7_bsmUQG8VQiPmcU5WemBJNh3MXNQB0GxODEdrrMH1aeswZBocSoB0v9FzzzPmupq1o88onKq7p_kVNzyI455700BjHjCdUqLEUKac1y3dsAkUEzAVOGRNLwWIZC6t1SyvRaXeLZzt8yf-dWsX37a7b-tXnrBPcZqy6LJEF2AAV9iM-4SikmMr49hnkG02cWQ7GcQDtmOQQR6IR1FXHxap2HeJ-SqIXHKC0K71f9k4MoqcTg2YMvphi08IiLi06Z4k5e9wEFJOGsfjiJGGB-E2KytWNIcgpwJsmj8YT0nOa8meWSh7JdzdzhxORET8VBpT6196TmW1cTrMeSHCkFgJFG4ova5A5ViQDqe7oSukYDOLKkU_jF0JceH9yWFJRDWu_9TLJpff9n7sOhF56-FbL-vr5YA90BMUqOA1G-jnqGi8mlDjaQoUpYJmoO9uqX9GPkWTBPSKqPuitmQp9Zttez9x9o-U8ya_fHF4_AHd4qNfAep5Ljr6AgJW349nasPabMmzN5eIyOy8j4GfCuUPjVuZC809boUga1pnPKLtGBGWL0oIpfZ2VxkBHI-u99CuSo0e3O9pRSV5g35yF-tIpQckySZeUh4tehk_Azui2TQeYOXXbrjRhNTv1k3PuPkGx52-wa4zirA5Y9GBoeuOVbaWV02JRsVyryrlVPTmE88rmwJzYpTtjqen4KlZ7CUbte-lhc5bJrLZc_ZW1LUclx7R_72Ny_h5YIZB2P6BfNZQdfMV3cCzi1fsk19ubbOMgJzpJatLpmXz2WStQWspGWYd61breDocFmQ05T5BAjrNYBpJ1_QVcCN4T81lUkzI5XuTSTbbs0NSNb2B-M8qWKaUKwi3Vf46sJ8UofJJ90cqOJnW5aFL6msO9oLgMTIN1VmHszJ0Qm9yihci8Bo-a3XUnbbSi7FcZii4NEHjz0ZetRXBs72wEqI8EdNr7oAv9OFwqXRS_Loj3lmwAT6Ocweaa59nbbdpwsWxYG1fKzjwuh5LYelqhBgBGZciRErHY1B_3v8CY58UeJtHocEOlFu1z1ymaYIlLvSL20hAdDhwt50X6R0v4goxzxXSX8eyRkjn4J78ba_HtotISQwYdu29bH-rrqIO07xPPj7GUGEwurbiYjLmT2O-vk001N29Lrh7zECep3wD3w42ccc1TPr_4DBsFHG-_0nZNLnbSE55kSk_21YRG9bxDK_RaNnv3FmizgsERGRJug6jFl9HVC_2KciHWsAohuk-au92Z7FxKg0gYM_Rp2YPREAQTMTY66VZu8I0JfodDGR76IY9Wc8oZ5CTgNjes2PQbodAmlMPe7cHUFhD8Kwe6dpqZ4pcqKFWdFZyI2cdfRuPig9EiOhLtprra9f8awRIaDgbF6lNXeUcnIpZ1DtdwShedK7eYXJfj3sAYudICLCIKaITNclYDoxNOhdLI_4JjihlQtP1i6skIYoYckt2pi9GnB24E3d7QuIZQiUnkMURIPHRU4t4A90IWcnCNQItK2ksRsue8GqOkDyv5w1zRWqOknMmC9z4E9zWgykRZto0nTnj-MtW9z-aLZNn88SBoLknRJRTQOrDJe_VWA5Nyovwb8D4nESia6r1NfCn74e0DwtlWKxUYsA-Xn39_xV2M5I49HFwk2ztTMK15n9RnGT_5oyJXit7POOWd2O6eiiMQca8QTJyji7qkQ-BD_6IQ6eRSC3yeOwZSdQVr9EGX9XeBNneUYqv5094ESTEz1191cKKDDoXv2Lj2kg12Ry1g_kTkY9mBnb2Nwy0Rq6GobA_D6fuYgA9Nk7q9kinLH2DQKDQ_fGs8wA5Ipc08zXRsCeHZ4g1S0tLmK1IVxqTKOiTbOlzzn3ynjaIRFfSvc4Z7_vDJEFnH8_ldDHoZh8bm8s81RupuqargSch5S51yh9ivbjkvPthwR6Dd-KTWT7AlH3QijVGRMWO_5zUP_Y0AhjGp9BJyXYohVXarMbTUTuJ8B2b1OC5_ZiAWLj3nhJWvq5one-TTEhTZ4bQJ7R69V3v4PodD2eravr47yhfSsbOUON_my_H29BzQmlkE2O36Nzv6VYVnclFQiyqXMtUqUdxXz16CI1BDG613uE-zwDOFwhdN9T1J4FIveY1_6DAIQEJPaQQLVoiNYkirODp0HO1-pjmMpyjnug9G64UxIs7OZ9PhcbXb6iYdySWWBLqwjo4jORjlcPL5VTqI_PN0N-05nPo-FsOa8XaCzwF_mMlHa327NcRDWxq6RuTN1AH8axynDWh466vIm1rOkFcLH21ixjqWpAePwxHS8cIBFRE97T7BJzmkhYcc18hFhL9Xjyq3U5hgXJVP_KrVMNiotzxewhMH8NuMGkn5a_Aw45L_Lf1VvYf3xbFh2-AZ3bPc_I-MD_rSn03Df8voLU4C3Gj0flCjQbD1W9hl13pzfchGoppcMdKXQoLHEi3P1RjDmvsUcIBOXLQE9U2SZqgHvK03jN5I0bbCAQe2AGY2-ruTbvGbopW-dQUVD5tZQWYxEAeE0ZQSz8eLOIBlr9AXUQSYllinzoabtWGjR97iWm8iZAgH_sv48GS9ONhwnEM9SpcXdCjQo0HVd43Zooaz9czdZtlULk80BCSxIj6XquxdqvBZqYsDTG0paqb-uxG2YPbwfhamRH4-w-n3vZyTO-Cm7LAqAchL3V26eqcYiK_ZaO1EvOLgj4w2eof19njzhXcYU2Z1Nlb59BBCYGpympps15y9O_YZfwzYw2SH5BesbpMO61cHJAuGrKiQWIMxbhmwfS1FBiukduitZBrgPPcqJEbryUYCaP9cNbtBt1gm7yXHpzTWSNbP3Ssik-NXXhPCaQQEwrDyCepGhXSKCY0nbAR_jSjw5IoGbtIxbMknJcTFVYnPnW_TqIPYNXpGkTo1_jdSK4Bqlnu4Y-btlZ2B2eoiokkwRcEpk69lUCABLZ3liFRRkv-q-59ziNxu06kl82ATg4OETUY-m5tyTaMvPD3hsA-Njt6CZ-ftgyzfKiEV87g2yCwesOec5wrwVlTZa_yPKNwfvTC2T04b9Sv1CdeNhtFJVLOluRhBav8hLrfAhnWpoAtdXBGUMtQFTLqaAd3UVeXCH2q80ay04hQulMBkF254BEgvcebaAalvx8wLsWkHcQ-0lUyE-SsvusSfMLrAC_NlUnT2_ANWZEb1zTHayw-kXHeqCsw8ZZx27_PEGkEki_tRcBpNd7SOVWhVxmXE6qxXX3lYtatEcxTpSvXrpOIxVG79ANcAbl8lveiY1YoD3E-Dbndv6Dznw3rtikRtUlGMlJYdSJlFZxgUkmYbn59aatte4r|regm\",\"waterfall_id\":\"7e11810e-9900-47f3-894d-86f61d266178\",\"INTERNAL__latency_qpl_instance_id\":1.24411143600028E14,\"flow_info\":\"{\\\"flow_name\\\":\\\"new_to_family_ig_default\\\",\\\"flow_type\\\":\\\"ntf\\\"}\",\"is_platform_login\":0,\"INTERNAL__latency_qpl_marker_id\":36707139,\"reg_info\":\"{}\",\"family_device_id\":\"97b3895a-649d-40f8-a516-e63aae231f80\",\"offline_experiment_group\":\"caa_launch_ig4a_combined_60_percent\",\"suggestions_container_id\":124411143600024,\"action\":1,\"screen_id\":124411143600002,\"access_flow_version\":\"pre_mt_behavior\",\"post_tos\":1,\"input_id\":124411143600026,\"is_from_logged_in_switcher\":0,\"current_step\":13,\"qe_device_id\":\"3b67cd48-7663-488d-8509-4caf099a935e\"}}",
            "_uuid": "3b67cd48-7663-488d-8509-4caf099a935e",
            "bk_client_context": "{\"bloks_version\":\"8ca96ca267e30c02cf90888d91eeff09627f0e3fd2bd9df472278c9a6c022cbb\",\"styles_id\":\"instagram\"}",
            "bloks_versioning_id": "8ca96ca267e30c02cf90888d91eeff09627f0e3fd2bd9df472278c9a6c022cbb"
        }
        xlol = requests.post(burp0_url, headers=burp0_headers, cookies={"sessionid": sessid}, data=burp0_data)
        bot.send_message(chat_id, f"✅ تم تنفيذ العملية على المستخدم @{username}")
    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ أثناء التنفيذ: {str(e)}")

def change_fullname(chat_id, sessid, fullname):
    try:
        url = "https://i.instagram.com/api/v1/accounts/edit_profile/"
        headers = {
            "User-Agent": "Instagram 123.1.0.26.114 (iPhone 12 ProMax)",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Host": "i.instagram.com",
        }
        data = {
            "first_name": fullname,
            "full_name": fullname,
            # يمكن إضافة حقول أخرى إذا لزم الأمر مثل username, email, إلخ
        }
        response = requests.post(url, headers=headers, cookies={"sessionid": sessid}, data=data)
        if response.status_code == 200 and "full_name" in response.text:
            bot.send_message(chat_id, f"✅ تم تغيير الاسم بنجاح إلى: {fullname}")
        else:
            bot.send_message(chat_id, "❌ فشل تغيير الاسم. تحقق من SessionID أو حاول لاحقاً.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ أثناء تغيير الاسم: {str(e)}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("تغيير الاسم", callback_data="change_name")
    )
    bot.send_message(chat_id, "👋 أهلاً بك في بوت انستقرام!\nالمطور: @kakkii\nاختر وظيفة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "change_name":
        user_states[chat_id] = {'step': 'ask_sessionid'}
        bot.send_message(chat_id, "🔑 أرسل SessionID الخاص بك:")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'ask_sessionid')
def receive_sessionid(message):
    chat_id = message.chat.id
    sessid = message.text.strip()
    user_states[chat_id] = {'sessid': sessid, 'step': 'ask_fullname'}
    bot.send_message(chat_id, "📝 أرسل الاسم الجديد الذي تريده:")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'ask_fullname')
def receive_fullname(message):
    chat_id = message.chat.id
    fullname = message.text.strip()
    sessid = user_states[chat_id]['sessid']
    bot.send_message(chat_id, f"⏳ جاري تغيير الاسم إلى {fullname} ...")
    thread = threading.Thread(target=change_fullname, args=(chat_id, sessid, fullname))
    thread.start()
    user_states[chat_id]['step'] = None

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url='https://amirli.onrender.com/webhook')
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
