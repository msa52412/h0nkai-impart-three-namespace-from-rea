// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 443209

/* ================= 0x1835D7F80 ================= */
/* name   = IsPatched */
/* entry  = 1835d7f80 */
/* body   = 146 bytes */
/* sig    = byte IsPatched(int id) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: bool WrappersManagerImpl::IsPatched(int id)  [static]  token=0603900B */

byte IFix::WrappersManagerImpl::IsPatched(int id)

{
  longlong lVar1;
  undefined8 uVar2;
  
  if (*(int *)(_DAT_189a34088 + 0xe8) == 0) {
    il2cpp::codegen::runtime_class_init();
  }
  if (**(longlong **)(_DAT_189a34088 + 0x28) == 0) {
                    /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  if (*(int *)(**(longlong **)(_DAT_189a34088 + 0x28) + 0x18) <= id) {
    return 0;
  }
  if (*(int *)(_DAT_189a34088 + 0xe8) == 0) {
    il2cpp::codegen::runtime_class_init();
  }
  lVar1 = **(longlong **)(_DAT_189a34088 + 0x28);
  if (lVar1 != 0) {
    if ((uint)id < *(uint *)(lVar1 + 0x18)) {
      return *(longlong *)(lVar1 + 0x20 + (longlong)id * 8) != 0;
    }
    uVar2 = il2cpp::codegen::get_index_out_of_range_exception();
                    /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_exception(uVar2,0);
  }
                    /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}



/* ================= 0x186637860 ================= */
/* name   = _ctor */
/* entry  = 186637860 */
/* body   = 288 bytes */
/* sig    = void _ctor(BulletinActivityConfig * this) */


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
  puVar1 = (undefined *)il2cpp::codegen::initialize_class(_DAT_1899e69f0);
  FUN_1849b2bc0(puVar1,0);
  this->mission_ids = puVar1;
  puVar1 = (undefined *)il2cpp::codegen::initialize_class(_DAT_1899e69f0);
  FUN_1849b2bc0(puVar1,0);
  this->type_param_list = puVar1;
  this->type_param_str = _DAT_189b4a238;
  this->min_player_level = 0;
  this->max_player_level = 0;
  puVar1 = (undefined *)il2cpp::codegen::initialize_class(_DAT_1899e69f0);
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
  puVar1 = (undefined *)il2cpp::codegen::initialize_class(_DAT_1899e69f0);
  FUN_1849b2bc0(puVar1,0);
  this->currency_list = puVar1;
  this->unlock_param_str = _DAT_189b4a238;
  return;
}



/* ================= 0x186B07D20 ================= */
/* name   = _ctor */
/* entry  = 186b07d20 */
/* body   = 219 bytes */
/* sig    = void _ctor(PlayerLoginReq * this) */


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
  this->device_type = 0;
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



