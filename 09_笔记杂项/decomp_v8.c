// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 443209

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



/* ================= 0x18052E070 ================= */
/* name   = AddOnePoint */
/* entry  = 18052e070 */
/* body   = 388 bytes */
/* sig    = void AddOnePoint(AreaData * this, PointData * pointData) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void AreaData::AddOnePoint(PointData pointData)  token=0600EA67 */

void AreaData::AddOnePoint(AreaData *this,PointData *pointData)

{
  undefined *puVar1;
  code *pcVar2;
  byte bVar3;
  char cVar4;
  uint uVar5;
  int iVar6;
  SecurityParser *this_00;
  MOHAFPKIFEP *pMVar7;
  ILFixDynamicMethodWrapper *this_01;
  SmallXmlParser *parser;
  SecurityParser *pSStackX_18;
  
  pSStackX_18 = (SecurityParser *)0x0;
  bVar3 = IFix::WrappersManagerImpl::IsPatched(0xdc4e);
  if (bVar3 != 0) {
    this_01 = IFix::WrappersManagerImpl::GetPatch(0xdc4e);
    if (this_01 != (ILFixDynamicMethodWrapper *)0x0) {
      IFix::ILFixDynamicMethodWrapper::Gen_Wrap_15(this_01,(undefined *)this,(undefined *)pointData)
      ;
      return;
    }
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    (*pcVar2)();
    return;
  }
  if ((pointData != (PointData *)0x0) && ((JJGEGLJILLD *)pointData->meta != (JJGEGLJILLD *)0x0)) {
    pSStackX_18 = (SecurityParser *)0x0;
    puVar1 = this->AreaId2AreaItemDic;
    uVar5 = MoleMole::ExcelMeta::JJGEGLJILLD::BIAMGOPAJBH((JJGEGLJILLD *)pointData->meta);
    if (puVar1 == (undefined *)0x0) {
      FUN_1804fe400();
      pcVar2 = (code *)swi(3);
      (*pcVar2)();
      return;
    }
    parser = (SmallXmlParser *)(ulonglong)uVar5;
    cVar4 = FUN_184d6cf50(puVar1,parser,&pSStackX_18,_DAT_189a9bc40);
    if (cVar4 == '\0') {
      this_00 = (SecurityParser *)thunk_FUN_1804457f0(_DAT_189a17568);
      Mono::Xml::SecurityParser::probe_1826b9250(this_00,parser);
      if ((JJGEGLJILLD *)pointData->meta == (JJGEGLJILLD *)0x0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      iVar6 = MoleMole::ExcelMeta::JJGEGLJILLD::BIAMGOPAJBH((JJGEGLJILLD *)pointData->meta);
      if (*(int *)(_DAT_1899efa80 + 0xe8) == 0) {
        thunk_FUN_18042d860();
      }
      pMVar7 = MoleMole::ExcelMeta::LIKDMCBPNDN::CPANAKCHPFA((byte)iVar6);
      if (this_00 == (SecurityParser *)0x0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      this_00->elementNames = (undefined *)pMVar7;
      puVar1 = this->AreaId2AreaItemDic;
      pSStackX_18 = this_00;
      if ((JJGEGLJILLD *)pointData->meta == (JJGEGLJILLD *)0x0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      iVar6 = MoleMole::ExcelMeta::JJGEGLJILLD::BIAMGOPAJBH((JJGEGLJILLD *)pointData->meta);
      if (puVar1 == (undefined *)0x0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      FUN_184d55310(puVar1,iVar6,pSStackX_18,_DAT_189a9bc48);
    }
    if (pSStackX_18 == (SecurityParser *)0x0) {
      FUN_1804fe400();
      pcVar2 = (code *)swi(3);
      (*pcVar2)();
      return;
    }
    AreaDataItem::AddOnePoint((AreaDataItem *)pSStackX_18,pointData);
  }
  return;
}



/* ================= 0x18052E320 ================= */
/* name   = GetArea */
/* entry  = 18052e320 */
/* body   = 143 bytes */
/* sig    = AreaDataItem * GetArea(AreaData * this, int areaId) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: AreaDataItem AreaData::GetArea(int areaId)  token=0600EA69 */

AreaDataItem * AreaData::GetArea(AreaData *this,int areaId)

{
  code *pcVar1;
  byte bVar2;
  ILFixDynamicMethodWrapper *this_00;
  AreaDataItem *pAVar3;
  AreaDataItem *apAStackX_18 [2];
  
  apAStackX_18[0] = (AreaDataItem *)0x0;
  bVar2 = IFix::WrappersManagerImpl::IsPatched(0xdcb3);
  if (bVar2 != 0) {
    this_00 = IFix::WrappersManagerImpl::GetPatch(0xdcb3);
    if (this_00 != (ILFixDynamicMethodWrapper *)0x0) {
      pAVar3 = IFix::ILFixDynamicMethodWrapper::Gen_Wrap_6532
                         ((ILFixDynamicMethodWrapper_57479 *)this_00,(undefined *)this,areaId);
      return pAVar3;
    }
    FUN_1804fe400();
    pcVar1 = (code *)swi(3);
    pAVar3 = (AreaDataItem *)(*pcVar1)();
    return pAVar3;
  }
  apAStackX_18[0] = (AreaDataItem *)0x0;
  if (this->AreaId2AreaItemDic != (undefined *)0x0) {
    FUN_184d6cf50(this->AreaId2AreaItemDic,areaId,apAStackX_18,_DAT_189a9bc40);
    return apAStackX_18[0];
  }
  FUN_1804fe400();
  pcVar1 = (code *)swi(3);
  pAVar3 = (AreaDataItem *)(*pcVar1)();
  return pAVar3;
}



/* ================= 0x18015CF320 ================= */
// no function defined at or containing 0x18015CF320

/* ================= 0x1801917F10 ================= */
// no function defined at or containing 0x1801917F10

