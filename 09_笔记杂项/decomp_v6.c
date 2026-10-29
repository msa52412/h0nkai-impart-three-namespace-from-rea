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



/* ================= 0x18052E910 ================= */
/* name   = _ctor */
/* entry  = 18052e910 */
/* body   = 12 bytes */
/* sig    = void _ctor(CCAGLJPMIFF * this, BaseActor * ONFGPPJOPHI, uint EDHEEBHCKMA, uint CCJMFKHNPGK) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void CCAGLJPMIFF::_ctor(MoleMole.BaseActor ONFGPPJOPHI, uint EDHEEBHCKMA, uint CCJMFKHNPGK)
   token=060034CB
   GENERIC-SHARED aliases (1): MoleMole.PlatformShooter::PlatformShooterDailyTicketInfo::_ctor;  */

void CCAGLJPMIFF::_ctor(CCAGLJPMIFF *this,BaseActor *ONFGPPJOPHI,uint EDHEEBHCKMA,uint CCJMFKHNPGK)

{
  this->JIIGDMPCAHE = (undefined *)ONFGPPJOPHI;
  this->HNFNEEHLFHE = EDHEEBHCKMA;
  this->EJMLAFBBMPH = CCJMFKHNPGK;
  return;
}



/* ================= 0x18052F7F0 ================= */
/* name   = GetAreaByID */
/* entry  = 18052f7f0 */
/* body   = 159 bytes */
/* sig    = GEAreaData * GetAreaByID(GEMapDataItem * this, int areaID) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: MoleMole_GlobalExplore_GEAreaData GEMapDataItem::GetAreaByID(int areaID)  token=0602FE95 */

GEAreaData * MoleMole::GlobalExplore::GEMapDataItem::GetAreaByID(GEMapDataItem *this,int areaID)

{
  undefined *puVar1;
  longlong lVar2;
  code *pcVar3;
  byte bVar4;
  char cVar5;
  uint uVar6;
  ILFixDynamicMethodWrapper *pIVar7;
  Call *pCVar8;
  KeyNotFoundException *this_00;
  undefined8 uVar9;
  GEAreaData *pGVar10;
  Call CStack_58;
  undefined8 uStack_30;
  
  uStack_30 = 0x18052f809;
  bVar4 = IFix::WrappersManagerImpl::IsPatched(0x9f05);
  if (bVar4 != 0) {
    uStack_30 = 0x18052f860;
    pIVar7 = IFix::WrappersManagerImpl::GetPatch(0x9f05);
    if (pIVar7 == (ILFixDynamicMethodWrapper *)0x0) {
      uStack_30 = 0x18052f88e;
      FUN_1804fe400();
      pcVar3 = (code *)swi(3);
      pGVar10 = (GEAreaData *)(*pcVar3)();
      return pGVar10;
    }
    CStack_58.argumentBase = (undefined *)0x0;
    CStack_58.evaluationStackBase = (undefined *)0x0;
    CStack_58.managedStack = (undefined *)0x0;
    CStack_58.currentTop = (undefined *)0x0;
    CStack_58.topWriteBack = (undefined *)0x0;
    pCVar8 = IFix::Core::Call::Begin();
    CStack_58.argumentBase = pCVar8->argumentBase;
    CStack_58.evaluationStackBase = pCVar8->evaluationStackBase;
    CStack_58.managedStack = pCVar8->managedStack;
    CStack_58.currentTop = pCVar8->currentTop;
    CStack_58.topWriteBack = pCVar8->topWriteBack;
    if (pIVar7->anonObj != (undefined *)0x0) {
      IFix::Core::Call::PushObject(&CStack_58,pIVar7->anonObj);
    }
    IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
    IFix::Core::Call::PushInt32(&CStack_58,areaID);
    if ((VirtualMachine *)pIVar7->virtualMachine != (VirtualMachine *)0x0) {
      IFix::Core::VirtualMachine::Execute
                ((VirtualMachine *)pIVar7->virtualMachine,pIVar7->methodId,&CStack_58,
                 (pIVar7->anonObj != (undefined *)0x0) + 2,0);
      pGVar10 = (GEAreaData *)FUN_18347f130(&CStack_58,0,_DAT_189adb1e8);
      return pGVar10;
    }
    FUN_1804fe400();
    pcVar3 = (code *)swi(3);
    pGVar10 = (GEAreaData *)(*pcVar3)();
    return pGVar10;
  }
  if (this->areaGlobalTiles == (undefined *)0x0) {
    uStack_30 = 0x18052f888;
    FUN_1804fe400();
    pcVar3 = (code *)swi(3);
    pGVar10 = (GEAreaData *)(*pcVar3)();
    return pGVar10;
  }
  uStack_30 = 0x18052f824;
  cVar5 = FUN_184d554c0(this->areaGlobalTiles,areaID,_DAT_189a9ba88);
  if (cVar5 == '\0') {
    return (GEAreaData *)0x0;
  }
  puVar1 = this->areaGlobalTiles;
  if (puVar1 == (undefined *)0x0) {
    uStack_30 = 0x18052f882;
    FUN_1804fe400();
    pcVar3 = (code *)swi(3);
    pGVar10 = (GEAreaData *)(*pcVar3)();
    return pGVar10;
  }
  if (puVar1 == (undefined *)0x0) {
    uStack_30 = 0x184d75319;
    FUN_1804fe400(0,areaID);
    pcVar3 = (code *)swi(3);
    pGVar10 = (GEAreaData *)(*pcVar3)();
    return pGVar10;
  }
  uStack_30 = 0x184d752b4;
  uVar6 = FUN_184d58230(puVar1,areaID,*(undefined8 *)(*(longlong *)(*_DAT_189a9ba90 + 0x90) + 0x88))
  ;
  if ((int)uVar6 < 0) {
    uStack_30 = 0x184d752e3;
    this_00 = (KeyNotFoundException *)thunk_FUN_1804457f0(_DAT_1899e0068);
    uStack_30 = 0x184d752ee;
    System::Collections::Generic::KeyNotFoundException::_ctor(this_00);
    uStack_30 = 0x184d752fd;
    FUN_1804fe3d0(this_00,_DAT_189a6e8c8);
    pcVar3 = (code *)swi(3);
    pGVar10 = (GEAreaData *)(*pcVar3)();
    return pGVar10;
  }
  lVar2 = *(longlong *)(puVar1 + 0x18);
  if (lVar2 != 0) {
    if (uVar6 < *(uint *)(lVar2 + 0x18)) {
      return *(GEAreaData **)(lVar2 + 0x30 + (longlong)(int)uVar6 * 0x18);
    }
    uStack_30 = 0x184d75303;
    uVar9 = thunk_FUN_180436120();
    uStack_30 = 0x184d7530d;
    FUN_1804fe3d0(uVar9,0);
    pcVar3 = (code *)swi(3);
    pGVar10 = (GEAreaData *)(*pcVar3)();
    return pGVar10;
  }
  uStack_30 = 0x184d75313;
  FUN_1804fe400();
  pcVar3 = (code *)swi(3);
  pGVar10 = (GEAreaData *)(*pcVar3)();
  return pGVar10;
}



/* ================= 0x18052EAF0 ================= */
/* name   = Reset */
/* entry  = 18052eaf0 */
/* body   = 204 bytes */
/* sig    = void Reset(DamageSection * this, BattlerModel * initiator) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void DamageSection::Reset(MoleMole.HoukaiTown.BattlerModel initiator)  token=0602C2C9 */

void MoleMole::HoukaiTown::DamageSection::Reset(DamageSection *this,BattlerModel *initiator)

{
  longlong *plVar1;
  code *pcVar2;
  byte bVar3;
  int iVar4;
  ILFixDynamicMethodWrapper *pIVar5;
  Call *pCVar6;
  Call CStack_58;
  undefined8 uStack_30;
  
  uStack_30 = 0x18052eb0a;
  bVar3 = IFix::WrappersManagerImpl::IsPatched(0x1fb92);
  if (bVar3 != 0) {
    uStack_30 = 0x18052eb87;
    pIVar5 = IFix::WrappersManagerImpl::GetPatch(0x1fb92);
    if (pIVar5 == (ILFixDynamicMethodWrapper *)0x0) {
      uStack_30 = 0x18052ebbb;
      FUN_1804fe400();
      pcVar2 = (code *)swi(3);
      (*pcVar2)();
      return;
    }
    CStack_58.argumentBase = (undefined *)0x0;
    CStack_58.evaluationStackBase = (undefined *)0x0;
    CStack_58.managedStack = (undefined *)0x0;
    CStack_58.currentTop = (undefined *)0x0;
    CStack_58.topWriteBack = (undefined *)0x0;
    pCVar6 = IFix::Core::Call::Begin();
    CStack_58.argumentBase = pCVar6->argumentBase;
    CStack_58.evaluationStackBase = pCVar6->evaluationStackBase;
    CStack_58.managedStack = pCVar6->managedStack;
    CStack_58.currentTop = pCVar6->currentTop;
    CStack_58.topWriteBack = pCVar6->topWriteBack;
    if (pIVar5->anonObj != (undefined *)0x0) {
      IFix::Core::Call::PushObject(&CStack_58,pIVar5->anonObj);
    }
    IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
    IFix::Core::Call::PushObject(&CStack_58,(undefined *)initiator);
    if ((VirtualMachine *)pIVar5->virtualMachine != (VirtualMachine *)0x0) {
      IFix::Core::VirtualMachine::Execute
                ((VirtualMachine *)pIVar5->virtualMachine,pIVar5->methodId,&CStack_58,
                 (pIVar5->anonObj != (undefined *)0x0) + 2,0);
      return;
    }
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    (*pcVar2)();
    return;
  }
  if (initiator == (BattlerModel *)0x0) {
    uStack_30 = 0x18052ebb5;
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    (*pcVar2)();
    return;
  }
  this->damage = initiator->attack;
  plVar1 = (longlong *)initiator->battler;
  if (plVar1 != (longlong *)0x0) {
    uStack_30 = 0x18052eb3a;
    iVar4 = (**(code **)(*plVar1 + 0x278))(plVar1,*(undefined8 *)(*plVar1 + 0x280));
    this->power = iVar4 + 100;
    plVar1 = (longlong *)initiator->battler;
    if (plVar1 != (longlong *)0x0) {
      uStack_30 = 0x18052eb59;
      iVar4 = (**(code **)(*plVar1 + 0x288))(plVar1,*(undefined8 *)(*plVar1 + 0x290));
      this->finalConst = 0;
      this->vulnerable = iVar4 + 100;
      this->critRate = initiator->critRate;
      this->critDamage = initiator->critDamage;
      return;
    }
    uStack_30 = 0x18052eba9;
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    (*pcVar2)();
    return;
  }
  uStack_30 = 0x18052ebaf;
  FUN_1804fe400();
  pcVar2 = (code *)swi(3);
  (*pcVar2)();
  return;
}



