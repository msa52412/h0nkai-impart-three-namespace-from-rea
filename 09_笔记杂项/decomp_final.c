// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 443209

/* ================= 0x186637860 ================= */
/* name   = _ctor */
/* entry  = 186637860 */
/* body   = 288 bytes */
/* sig    = undefined _ctor(BulletinActivityConfig * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void BulletinActivityConfig::_ctor()  token=0600008B */

void proto::BulletinActivityConfig::_ctor(BulletinActivityConfig *this)

{
  undefined *puVar1;
  
  this->activity_id = 0;
  this->activity_type = 0;
  this->begin_time = 0;
  this->end_time = 0;
  this->bulletin_id = 0;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(puVar1,0);
  this->mission_ids = puVar1;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(puVar1,0);
  this->type_param_list = puVar1;
  this->type_param_str = _DAT_189b4a238;
  this->min_player_level = 0;
  this->max_player_level = 0;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(puVar1,0);
  this->item_list = puVar1;
  this->title_name = _DAT_189b4a238;
  this->title_image = _DAT_189b4a238;
  this->image_path = _DAT_189b4a238;
  this->link_button = _DAT_189b4a238;
  this->description = _DAT_189b4a238;
  this->weight = 0;
  this->background_path = _DAT_189b4a238;
  this->text_image_path = _DAT_189b4a238;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(puVar1,0);
  this->currency_list = puVar1;
  this->unlock_param_str = _DAT_189b4a238;
  return;
}



/* ================= 0x186AF8990 ================= */
/* name   = _ctor */
/* entry  = 186af8990 */
/* body   = 525 bytes */
/* sig    = undefined _ctor(OpenworldChapter * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void OpenworldChapter::_ctor()  token=06000139 */

void proto::OpenworldChapter::_ctor(OpenworldChapter *this)

{
  undefined *puVar1;
  
  this->map_id = 0;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e9688);
  FUN_184fb8fa0(puVar1,_DAT_189a74530);
  this->slot_list = puVar1;
  this->max_equip_cost = 0;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e9690);
  FUN_184fb8fa0(puVar1,_DAT_189a74538);
  this->buff_list = puVar1;
  this->max_reward_take_num = 0;
  this->fame = 0;
  this->fame_level = 0;
  this->challenge = (undefined *)0x0;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e9698);
  FUN_184fb8fa0(puVar1,_DAT_189a74540);
  this->endless_tower_site_list = puVar1;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e96a0);
  FUN_184fb8fa0(puVar1,_DAT_189a74548);
  this->hero_list = puVar1;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e96a8);
  FUN_184fb8fa0(puVar1,_DAT_189a74550);
  this->hero_card_list = puVar1;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e96b0);
  FUN_184fb8fa0(puVar1,_DAT_189a74558);
  this->hero_card_group_list = puVar1;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e96b8);
  FUN_184fb8fa0(puVar1,_DAT_189a74560);
  this->achievement_mission_list = puVar1;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e96c0);
  FUN_184fb8fa0(puVar1,_DAT_189a74568);
  this->endless_challenge_list = puVar1;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e96c8);
  FUN_184fb8fa0(puVar1,_DAT_189a74570);
  this->building_list = puVar1;
  this->terminal = (undefined *)0x0;
  this->quest_data = (undefined *)0x0;
  this->furnace = (undefined *)0x0;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e96d0);
  FUN_184fb8fa0(puVar1,_DAT_189a74578);
  this->talent_list = puVar1;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(puVar1,0);
  this->active_talent_id_list = puVar1;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e96d8);
  FUN_184fb8fa0(puVar1,_DAT_189a74580);
  this->dig_site_list = puVar1;
  puVar1 = (undefined *)thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(puVar1,0);
  this->got_last_reward_special_qte_map_list = puVar1;
  return;
}



/* ================= 0x186B07D20 ================= */
/* name   = _ctor */
/* entry  = 186b07d20 */
/* body   = 219 bytes */
/* sig    = undefined _ctor(PlayerLoginReq * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void PlayerLoginReq::_ctor()  token=0600000B */

void proto::PlayerLoginReq::_ctor(PlayerLoginReq *this)

{
  this->last_server_packet_id = 0;
  this->cps = _DAT_189b4a238;
  this->check_sum = _DAT_189b4a238;
  this->device_uuid = _DAT_189b4a238;
  this->android_signatures = _DAT_189b4a238;
  this->language = _DAT_189b4a238;
  this->advertiser_id = _DAT_189b4a238;
  this->security_cmd_reply = (undefined *)0x0;
  this->last_login_version = 0;
  this->account_type = 0;
  this->account_uid = _DAT_189b4a238;
  this->pad_60[0] = 0;
  this->pad_60[1] = 0;
  this->pad_60[2] = 0;
  this->pad_60[3] = 0;
  this->user_type = 0;
  this->user_ip = _DAT_189b4a238;
  this->tag = 0;
  this->client_version = _DAT_189b4a238;
  this->client_device = _DAT_189b4a238;
  this->system_info = _DAT_189b4a238;
  this->android_sign = _DAT_189b4a238;
  this->limit_level = 0;
  this->black_list_end_time = 0;
  this->is_bind_access = 0;
  this->login_session_token = 0;
  this->hoyolab_account_uid = _DAT_189b4a238;
  this->user_port = 0;
  this->ua_pc = _DAT_189b4a238;
  return;
}



/* ================= 0x186B0A680 ================= */
/* name   = _ctor */
/* entry  = 186b0a680 */
/* body   = 231 bytes */
/* sig    = undefined _ctor(GetPlayerTokenReq * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void GetPlayerTokenReq::_ctor()  token=06000007 */

void proto::GetPlayerTokenReq::_ctor(GetPlayerTokenReq *this)

{
  this->account_uid = _DAT_189b4a238;
  this->account_token = _DAT_189b4a238;
  this->account_ext = _DAT_189b4a238;
  this->token = _DAT_189b4a238;
  this->version = _DAT_189b4a238;
  this->device = _DAT_189b4a238;
  this->tag = 0;
  this->uid = 0;
  this->system_info = _DAT_189b4a238;
  this->ipv4_str = _DAT_189b4a238;
  this->ipv6_str = _DAT_189b4a238;
  this->cps = _DAT_189b4a238;
  this->device_uuid = _DAT_189b4a238;
  this->transfer_code = _DAT_189b4a238;
  this->transfer_pwd = _DAT_189b4a238;
  this->ip_info_str = _DAT_189b4a238;
  *(undefined4 *)this->pad_90 = 0;
  this->is_allow_device_register = 0;
  this->combo_channel_id = 0;
  this->combo_token = _DAT_189b4a238;
  this->user_ip_str = _DAT_189b4a238;
  this->ua_pc = _DAT_189b4a238;
  return;
}



