// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 443209

/* ================= 0x18052E000 ================= */
/* name   = MEPEMDKMDNO */
/* entry  = 18052e000 */
/* body   = 61 bytes */
/* sig    = void MEPEMDKMDNO(ACADIAMONHG * this, byte FMMBEDDOBAA) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void ACADIAMONHG::MEPEMDKMDNO(bool FMMBEDDOBAA)  token=06002995 */

void ACADIAMONHG::MEPEMDKMDNO(ACADIAMONHG *this,byte FMMBEDDOBAA)

{
  code *pcVar1;
  char cVar2;
  MiHoYoGameData *this_00;
  longlong lVar3;
  MonoGameEntry *this_01;
  MonoTimerManager *this_02;
  ApplicationManager *this_03;
  longlong *plVar4;
  longlong lVar5;
  longlong lVar6;
  undefined8 uVar7;
  DMNJPBIJNIJ *this_04;
  undefined8 *puVar8;
  undefined7 in_register_00000011;
  undefined8 uVar9;
  ulonglong uVar10;
  Call CStack_58;
  undefined8 auStack_30 [5];
  
  if ((KCNIFKDJNFF *)this->NIMLNEHLEGP == (KCNIFKDJNFF *)0x0) {
    auStack_30[0] = 0x18052e03c;
    FUN_1804fe400(this,CONCAT71(in_register_00000011,FMMBEDDOBAA));
    pcVar1 = (code *)swi(3);
    (*pcVar1)();
    return;
  }
  auStack_30[0] = 0x18052e019;
  MoleMole::KCNIFKDJNFF::FOFDDCNNEBI((KCNIFKDJNFF *)this->NIMLNEHLEGP);
  if (*(int *)(_DAT_189a16b50 + 0xe8) == 0) {
    auStack_30[0] = 0x18052e02e;
    thunk_FUN_18042d860();
  }
  auStack_30[0] = 0x18179e54e;
  cVar2 = IFix::WrappersManagerImpl::IsPatched(0xdd3);
  if (cVar2 != '\0') {
    auStack_30[0] = 0x18179e92b;
    lVar3 = IFix::WrappersManagerImpl::GetPatch(0xdd3);
    if (lVar3 == 0) {
      auStack_30[0] = 0x18179e98f;
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    CStack_58.argumentBase = (undefined *)0x0;
    CStack_58.evaluationStackBase = (undefined *)0x0;
    CStack_58.managedStack = (undefined *)0x0;
    CStack_58.currentTop = (undefined *)0x0;
    CStack_58.topWriteBack = (undefined *)0x0;
    puVar8 = (undefined8 *)IFix::Core::Call::Begin(auStack_30);
    CStack_58.argumentBase = (undefined *)*puVar8;
    CStack_58.evaluationStackBase = (undefined *)puVar8[1];
    CStack_58.managedStack = (undefined *)puVar8[2];
    CStack_58.currentTop = (undefined *)puVar8[3];
    CStack_58.topWriteBack = (undefined *)puVar8[4];
    if (*(longlong *)(lVar3 + 0x20) != 0) {
      IFix::Core::Call::PushObject(&CStack_58);
    }
    if (*(VirtualMachine **)(lVar3 + 0x10) == (VirtualMachine *)0x0) {
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    IFix::Core::VirtualMachine::Execute(*(VirtualMachine **)(lVar3 + 0x10));
    return;
  }
  lVar3 = *_DAT_189a98410;
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e576;
    FUN_18043e4c0(lVar3);
  }
  lVar3 = **(longlong **)(lVar3 + 0x90);
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e591;
    FUN_18043e4c0(lVar3);
  }
  if (**(longlong **)(lVar3 + 0x28) == 0) {
    auStack_30[0] = 0x18179e989;
    FUN_1804fe400();
    pcVar1 = (code *)swi(3);
    (*pcVar1)();
    return;
  }
  plVar4 = *(longlong **)(**(longlong **)(lVar3 + 0x28) + 0x18);
  if (plVar4 == (longlong *)0x0) {
    auStack_30[0] = 0x18179e983;
    FUN_1804fe400();
    pcVar1 = (code *)swi(3);
    (*pcVar1)();
    return;
  }
  auStack_30[0] = 0x18179e5be;
  (**(code **)(*plVar4 + 0x3c8))(plVar4,*(undefined8 *)(*plVar4 + 0x3d0));
  if (*(int *)(_DAT_1899e6f70 + 0xe8) == 0) {
    auStack_30[0] = 0x18179e5d6;
    thunk_FUN_18042d860(_DAT_1899e6f70);
  }
  if (*(char *)(*(longlong *)(_DAT_1899e6f70 + 0x28) + 0xe8) != '\0') {
    return;
  }
  lVar3 = *_DAT_189a98398;
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e609;
    FUN_18043e4c0(lVar3);
  }
  lVar3 = **(longlong **)(lVar3 + 0x90);
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e624;
    FUN_18043e4c0(lVar3);
  }
  if (**(longlong **)(lVar3 + 0x28) != 0) {
    auStack_30[0] = 0x18179e63a;
    this_00 = (MiHoYoGameData *)FUN_180261460(_DAT_189a98398);
    if (this_00 == (MiHoYoGameData *)0x0) {
      auStack_30[0] = 0x18179e941;
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    auStack_30[0] = 0x18179e64d;
    MoleMole::MiHoYoGameData::SaveIfNeeded(this_00);
  }
  lVar3 = *_DAT_189a985c0;
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e668;
    FUN_18043e4c0(lVar3);
  }
  lVar3 = **(longlong **)(lVar3 + 0x90);
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e683;
    FUN_18043e4c0(lVar3);
  }
  if (**(longlong **)(lVar3 + 0x28) != 0) {
    auStack_30[0] = 0x18179e699;
    lVar3 = FUN_180261460(_DAT_189a985c0);
    if (lVar3 == 0) {
      auStack_30[0] = 0x18179e953;
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    auStack_30[0] = 0x18179e6ad;
    cVar2 = UnityEngine::Object::op_Inequality(*(undefined8 *)(lVar3 + 0x10),0);
    if (cVar2 != '\0') {
      auStack_30[0] = 0x18179e6bd;
      lVar3 = FUN_180261460(_DAT_189a985c0);
      if (lVar3 == 0) {
        auStack_30[0] = 0x18179e94d;
        FUN_1804fe400();
        pcVar1 = (code *)swi(3);
        (*pcVar1)();
        return;
      }
      auStack_30[0] = 0x18179e6d6;
      this_01 = (MonoGameEntry *)func_0x000180257760(*(undefined8 *)(lVar3 + 0x10),_DAT_189a15d68);
      auStack_30[0] = 0x18179e6e3;
      cVar2 = UnityEngine::Object::op_Inequality(this_01,0);
      if (cVar2 != '\0') {
        if (this_01 == (MonoGameEntry *)0x0) {
          auStack_30[0] = 0x18179e947;
          FUN_1804fe400();
          pcVar1 = (code *)swi(3);
          (*pcVar1)();
          return;
        }
        auStack_30[0] = 0x18179e6f8;
        MoleMole::MonoGameEntry::OnRestartGame(this_01);
      }
    }
  }
  auStack_30[0] = 0x18179e6fd;
  this_02 = (MonoTimerManager *)MoleMole::MonoTimerManager::get_Instance();
  if (this_02 == (MonoTimerManager *)0x0) {
    auStack_30[0] = 0x18179e97d;
    FUN_1804fe400();
    pcVar1 = (code *)swi(3);
    (*pcVar1)();
    return;
  }
  auStack_30[0] = 0x18179e70e;
  MoleMole::MonoTimerManager::RestartGame(this_02);
  if (*(int *)(_DAT_1899e6d18 + 0xe8) == 0) {
    auStack_30[0] = 0x18179e723;
    thunk_FUN_18042d860();
  }
  auStack_30[0] = 0x18179e728;
  MoleMole::RemoteTime::ClearInitStatus();
  lVar3 = *_DAT_189a98a58;
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e743;
    FUN_18043e4c0(lVar3);
  }
  lVar3 = **(longlong **)(lVar3 + 0x90);
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e75e;
    FUN_18043e4c0(lVar3);
  }
  if (**(longlong **)(lVar3 + 0x28) == 0) {
    auStack_30[0] = 0x18179e977;
    FUN_1804fe400();
    pcVar1 = (code *)swi(3);
    (*pcVar1)();
    return;
  }
  auStack_30[0] = 0x18179e773;
  MoleMole::WwiseAudioManager::StopAll();
  lVar3 = *_DAT_189a98a58;
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e78e;
    FUN_18043e4c0(lVar3);
  }
  lVar3 = **(longlong **)(lVar3 + 0x90);
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e7a9;
    FUN_18043e4c0(lVar3);
  }
  if (**(longlong **)(lVar3 + 0x28) == 0) {
    auStack_30[0] = 0x18179e971;
    FUN_1804fe400();
    pcVar1 = (code *)swi(3);
    (*pcVar1)();
    return;
  }
  auStack_30[0] = 0x18179e7be;
  MoleMole::WwiseAudioManager::ClearUp();
  lVar3 = *_DAT_189a98668;
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e7d9;
    FUN_18043e4c0(lVar3);
  }
  lVar3 = **(longlong **)(lVar3 + 0x90);
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e7f4;
    FUN_18043e4c0(lVar3);
  }
  if (**(longlong **)(lVar3 + 0x28) != 0) {
    auStack_30[0] = 0x18179e80a;
    lVar3 = FUN_180261460(_DAT_189a98668);
    if (lVar3 == 0) {
      auStack_30[0] = 0x18179e95f;
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    if (*(longlong *)(lVar3 + 0x48) == 0) {
      auStack_30[0] = 0x18179e959;
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    *(undefined4 *)(*(longlong *)(lVar3 + 0x48) + 0x18) = 0;
  }
  lVar3 = *_DAT_189a99490;
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e842;
    FUN_18043e4c0(lVar3);
  }
  lVar3 = **(longlong **)(lVar3 + 0x90);
  if (*(char *)(lVar3 + 0x136) == '\0') {
    auStack_30[0] = 0x18179e85d;
    FUN_18043e4c0(lVar3);
  }
  if (**(longlong **)(lVar3 + 0x28) != 0) {
    auStack_30[0] = 0x18179e873;
    this_03 = (ApplicationManager *)FUN_180261460(_DAT_189a99490);
    if (this_03 == (ApplicationManager *)0x0) {
      auStack_30[0] = 0x18179e965;
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    auStack_30[0] = 0x18179e884;
    MoleMole::ApplicationManager::StopAllCoroutines(this_03);
  }
  auStack_30[0] = 0x18179e890;
  cVar2 = FUN_183fba1b0(_DAT_189ac29b0);
  if (cVar2 != '\0') {
    auStack_30[0] = 0x18179e8a0;
    lVar3 = FUN_183fba070(_DAT_189a9ed60);
    if (lVar3 == 0) {
      auStack_30[0] = 0x18179e96b;
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    if (*(char *)(lVar3 + 0x5c) == '\0') {
      lVar3 = _DAT_189b8bd60;
      if (*(int *)(_DAT_189a15168 + 0xe8) == 0) {
        auStack_30[0] = 0x18179e8c4;
        thunk_FUN_18042d860();
        lVar3 = _DAT_189b8bd60;
      }
      goto UnityEngine_SceneManagement_SceneManager_LoadScene;
    }
  }
  lVar3 = _DAT_189bc8270;
  if (*(int *)(_DAT_189a15168 + 0xe8) == 0) {
    auStack_30[0] = 0x18179e902;
    thunk_FUN_18042d860();
    lVar3 = _DAT_189bc8270;
  }
UnityEngine_SceneManagement_SceneManager_LoadScene:
  lVar6 = _DAT_189b4a238;
  uVar10 = 0;
  auStack_30[0] = 0x182555603;
  cVar2 = IFix::WrappersManagerImpl::IsPatched(0xdde);
  if (cVar2 != '\0') {
    auStack_30[0] = 0x1825557bd;
    lVar5 = IFix::WrappersManagerImpl::GetPatch(0xdde);
    if (lVar5 == 0) {
      auStack_30[0] = 0x182555834;
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    CStack_58.argumentBase = (undefined *)0x0;
    CStack_58.evaluationStackBase = (undefined *)0x0;
    CStack_58.managedStack = (undefined *)0x0;
    CStack_58.currentTop = (undefined *)0x0;
    CStack_58.topWriteBack = (undefined *)0x0;
    puVar8 = (undefined8 *)IFix::Core::Call::Begin(auStack_30,lVar3,lVar6,0);
    CStack_58.argumentBase = (undefined *)*puVar8;
    CStack_58.evaluationStackBase = (undefined *)puVar8[1];
    CStack_58.managedStack = (undefined *)puVar8[2];
    CStack_58.currentTop = (undefined *)puVar8[3];
    CStack_58.topWriteBack = (undefined *)puVar8[4];
    if (*(longlong *)(lVar5 + 0x20) != 0) {
      IFix::Core::Call::PushObject(&CStack_58);
    }
    IFix::Core::Call::PushObject(&CStack_58);
    IFix::Core::Call::PushObject(&CStack_58);
    IFix::Core::Call::PushInt32(&CStack_58);
    if (*(VirtualMachine **)(lVar5 + 0x10) == (VirtualMachine *)0x0) {
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    IFix::Core::VirtualMachine::Execute(*(VirtualMachine **)(lVar5 + 0x10));
    return;
  }
  lVar5 = *_DAT_189a98fc0;
  if (*(char *)(lVar5 + 0x136) == '\0') {
    auStack_30[0] = 0x18255562b;
    FUN_18043e4c0(lVar5);
  }
  lVar5 = **(longlong **)(lVar5 + 0x90);
  if (*(char *)(lVar5 + 0x136) == '\0') {
    auStack_30[0] = 0x182555646;
    FUN_18043e4c0(lVar5);
  }
  uVar7 = _DAT_189bc5b70;
  if (**(longlong **)(lVar5 + 0x28) != 0) {
    auStack_30[0] = 0x182555668;
    cVar2 = System::String::IsNullOrEmpty(lVar6);
    if (cVar2 == '\0') {
      auStack_30[0] = 0x182555681;
      plVar4 = (longlong *)func_0x0001804fe0c0(_DAT_1899de718,2);
      if (plVar4 == (longlong *)0x0) {
        auStack_30[0] = 0x182555828;
        FUN_1804fe400();
        pcVar1 = (code *)swi(3);
        (*pcVar1)();
        return;
      }
      if (lVar6 != 0) {
        auStack_30[0] = 0x1825556a1;
        lVar5 = thunk_FUN_180442320(lVar6,*(undefined8 *)(*plVar4 + 0x30));
        if (lVar5 == 0) {
          auStack_30[0] = 0x1825557e8;
          uVar7 = thunk_FUN_180431fb0();
          auStack_30[0] = 0x1825557f2;
          FUN_1804fe3d0(uVar7,0);
          pcVar1 = (code *)swi(3);
          (*pcVar1)();
          return;
        }
      }
      if ((int)plVar4[3] == 0) {
        auStack_30[0] = 0x1825557f8;
        uVar7 = thunk_FUN_180436120();
        auStack_30[0] = 0x182555802;
        FUN_1804fe3d0(uVar7,0);
        pcVar1 = (code *)swi(3);
        (*pcVar1)();
        return;
      }
      plVar4[4] = lVar6;
      if (lVar3 != 0) {
        auStack_30[0] = 0x1825556cc;
        lVar6 = thunk_FUN_180442320(lVar3,*(undefined8 *)(*plVar4 + 0x30));
        if (lVar6 == 0) {
          auStack_30[0] = 0x182555808;
          uVar7 = thunk_FUN_180431fb0();
          auStack_30[0] = 0x182555812;
          FUN_1804fe3d0(uVar7,0);
          pcVar1 = (code *)swi(3);
          (*pcVar1)();
          return;
        }
      }
      if (*(uint *)(plVar4 + 3) < 2) {
        auStack_30[0] = 0x182555818;
        uVar7 = thunk_FUN_180436120();
        auStack_30[0] = 0x182555822;
        FUN_1804fe3d0(uVar7,0);
        pcVar1 = (code *)swi(3);
        (*pcVar1)();
        return;
      }
      plVar4[5] = lVar3;
      auStack_30[0] = 0x1825556ee;
      uVar7 = MoleMole::PathUtils::Combine(uVar7,plVar4);
    }
    else {
      auStack_30[0] = 0x1825556fb;
      uVar7 = MoleMole::PathUtils::Combine(uVar7,lVar3);
    }
    if (*(int *)(_DAT_189a15168 + 0xe8) == 0) {
      auStack_30[0] = 0x182555713;
      thunk_FUN_18042d860();
    }
    auStack_30[0] = 0x182555724;
    uVar9 = _DAT_189bc9b18;
    uVar7 = MoleMole::Miscs::GetAssetAsbFullPath(0,uVar7,_DAT_189bc9b18);
    lVar6 = *_DAT_189a98fc0;
    if (*(char *)(lVar6 + 0x136) == '\0') {
      auStack_30[0] = 0x182555742;
      FUN_18043e4c0(lVar6);
    }
    lVar6 = **(longlong **)(lVar6 + 0x90);
    if (*(char *)(lVar6 + 0x136) == '\0') {
      auStack_30[0] = 0x18255575d;
      FUN_18043e4c0(lVar6);
    }
    if (**(longlong **)(lVar6 + 0x28) == 0) {
      auStack_30[0] = 0x18255582e;
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      (*pcVar1)();
      return;
    }
    uVar10 = CONCAT71((int7)((ulonglong)uVar9 >> 8),1);
    auStack_30[0] = 0x182555778;
    this_04 = (DMNJPBIJNIJ *)
              MoleMole::StreamingAssetBundleManager::GetAsbInfoByAssetFullPath
                        (**(longlong **)(lVar6 + 0x28),uVar7,uVar10);
    if (this_04 != (DMNJPBIJNIJ *)0x0) {
      uVar10 = uVar10 & 0xffffffffffffff00;
      auStack_30[0] = 0x18255578e;
      MoleMole::DMNJPBIJNIJ::BHEGCIIPBAP(this_04);
    }
  }
                    /* WARNING: Could not recover jumptable at 0x0001868b5b2d. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*_DAT_1899d6168)(lVar3,0xffffffff,uVar10 & 0xffffffffffffff00,1);
  return;
}



/* ================= 0x18052E040 ================= */
/* name   = BNBHIELOPBG */
/* entry  = 18052e040 */
/* body   = 33 bytes */
/* sig    = byte BNBHIELOPBG(pointer this, Material * KOPNFGMFGBF) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: bool OIMEOKMDNPO::BNBHIELOPBG(proto.Material KOPNFGMFGBF)  token=0600D77B
   GENERIC-SHARED aliases (3): AMKOHHIPEMP::BDCOEALODDL; AMKOHHIPEMP::IDGKNBBGGHC;
   MoleMole::OCHOLKKOMCJ::RefreshStageRecord_b_26_0;  */

byte OIMEOKMDNPO::BNBHIELOPBG(undefined *this,Material *KOPNFGMFGBF)

{
  code *pcVar1;
  byte bVar2;
  
  if (KOPNFGMFGBF != (Material *)0x0) {
    return (ulonglong)KOPNFGMFGBF->id == (longlong)*(int *)(this + 0x14);
  }
  FUN_1804fe400();
  pcVar1 = (code *)swi(3);
  bVar2 = (*pcVar1)();
  return bVar2;
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
  char cVar3;
  undefined1 uVar4;
  undefined4 uVar5;
  SoapFieldAttribute *this_00;
  ILFixDynamicMethodWrapper *this_01;
  SoapFieldAttribute *pSStackX_18;
  
  pSStackX_18 = (SoapFieldAttribute *)0x0;
  cVar3 = IFix::WrappersManagerImpl::IsPatched(0xdc4e);
  if (cVar3 != '\0') {
    this_01 = (ILFixDynamicMethodWrapper *)IFix::WrappersManagerImpl::GetPatch(0xdc4e);
    if (this_01 != (ILFixDynamicMethodWrapper *)0x0) {
      IFix::ILFixDynamicMethodWrapper::Gen_Wrap_15(this_01);
      return;
    }
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    (*pcVar2)();
    return;
  }
  if ((pointData != (PointData *)0x0) && ((JJGEGLJILLD *)pointData->meta != (JJGEGLJILLD *)0x0)) {
    pSStackX_18 = (SoapFieldAttribute *)0x0;
    puVar1 = this->AreaId2AreaItemDic;
    uVar5 = MoleMole::ExcelMeta::JJGEGLJILLD::BIAMGOPAJBH((JJGEGLJILLD *)pointData->meta);
    if (puVar1 == (undefined *)0x0) {
      FUN_1804fe400();
      pcVar2 = (code *)swi(3);
      (*pcVar2)();
      return;
    }
    cVar3 = FUN_184d6cf50(puVar1,uVar5,&pSStackX_18,_DAT_189a9bc40);
    if (cVar3 == '\0') {
      this_00 = (SoapFieldAttribute *)thunk_FUN_1804457f0(_DAT_189a17568);
      Mono::Xml::SecurityParser::probe_1826b9250(this_00);
      if ((JJGEGLJILLD *)pointData->meta == (JJGEGLJILLD *)0x0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      uVar4 = MoleMole::ExcelMeta::JJGEGLJILLD::BIAMGOPAJBH((JJGEGLJILLD *)pointData->meta);
      if (*(int *)(_DAT_1899efa80 + 0xe8) == 0) {
        thunk_FUN_18042d860();
      }
      puVar1 = (undefined *)MoleMole::ExcelMeta::LIKDMCBPNDN::CPANAKCHPFA(uVar4);
      if (this_00 == (SoapFieldAttribute *)0x0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      this_00->ReflectInfo = puVar1;
      puVar1 = this->AreaId2AreaItemDic;
      pSStackX_18 = this_00;
      if ((JJGEGLJILLD *)pointData->meta == (JJGEGLJILLD *)0x0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      uVar5 = MoleMole::ExcelMeta::JJGEGLJILLD::BIAMGOPAJBH((JJGEGLJILLD *)pointData->meta);
      if (puVar1 == (undefined *)0x0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      FUN_184d55310(puVar1,uVar5,pSStackX_18,_DAT_189a9bc48);
    }
    if (pSStackX_18 == (SoapFieldAttribute *)0x0) {
      FUN_1804fe400();
      pcVar2 = (code *)swi(3);
      (*pcVar2)();
      return;
    }
    AreaDataItem::AddOnePoint((AreaDataItem *)pSStackX_18);
  }
  return;
}



/* ================= 0x18052E260 ================= */
/* name   = GetAreaState */
/* entry  = 18052e260 */
/* body   = 181 bytes */
/* sig    = uint GetAreaState(AreaData * this, int areaId) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: AreaState AreaData::GetAreaState(int areaId)  token=0600EA68 */

uint AreaData::GetAreaState(AreaData *this,int areaId)

{
  code *pcVar1;
  char cVar2;
  byte bVar3;
  uint uVar4;
  ILFixDynamicMethodWrapper_57479 *this_00;
  AreaDataItem *apAStackX_18 [2];
  
  apAStackX_18[0] = (AreaDataItem *)0x0;
  cVar2 = IFix::WrappersManagerImpl::IsPatched(0xdc8a);
  if (cVar2 != '\0') {
    this_00 = (ILFixDynamicMethodWrapper_57479 *)IFix::WrappersManagerImpl::GetPatch(0xdc8a);
    if (this_00 != (ILFixDynamicMethodWrapper_57479 *)0x0) {
      uVar4 = IFix::ILFixDynamicMethodWrapper::Gen_Wrap_5591(this_00);
      return uVar4;
    }
    FUN_1804fe400();
    pcVar1 = (code *)swi(3);
    uVar4 = (*pcVar1)();
    return uVar4;
  }
  bVar3 = 0;
  apAStackX_18[0] = (AreaDataItem *)0x0;
  if (this->AreaId2AreaItemDic != (undefined *)0x0) {
    cVar2 = FUN_184d6cf50(this->AreaId2AreaItemDic,areaId,apAStackX_18,_DAT_189a9bc40);
    if (cVar2 != '\0') {
      if (apAStackX_18[0] == (AreaDataItem *)0x0) {
        FUN_1804fe400();
        pcVar1 = (code *)swi(3);
        uVar4 = (*pcVar1)();
        return uVar4;
      }
      bVar3 = AreaDataItem::GetAreaState(apAStackX_18[0]);
    }
    return (uint)bVar3;
  }
  FUN_1804fe400();
  pcVar1 = (code *)swi(3);
  uVar4 = (*pcVar1)();
  return uVar4;
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
  char cVar2;
  ILFixDynamicMethodWrapper_57479 *this_00;
  AreaDataItem *pAVar3;
  AreaDataItem *apAStackX_18 [2];
  
  apAStackX_18[0] = (AreaDataItem *)0x0;
  cVar2 = IFix::WrappersManagerImpl::IsPatched(0xdcb3);
  if (cVar2 != '\0') {
    this_00 = (ILFixDynamicMethodWrapper_57479 *)IFix::WrappersManagerImpl::GetPatch(0xdcb3);
    if (this_00 != (ILFixDynamicMethodWrapper_57479 *)0x0) {
      pAVar3 = (AreaDataItem *)IFix::ILFixDynamicMethodWrapper::Gen_Wrap_6532(this_00);
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



/* ================= 0x18052E400 ================= */
/* name   = NNMFPNOELFD */
/* entry  = 18052e400 */
/* body   = 86 bytes */
/* sig    = void NNMFPNOELFD(BAHPEKDKFLE * this, JAHPKOOJOGP * GKDHBGOOKBH) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void BAHPEKDKFLE::NNMFPNOELFD(MoleMole.JAHPKOOJOGP GKDHBGOOKBH)  token=06014E40 */

void BAHPEKDKFLE::NNMFPNOELFD(BAHPEKDKFLE *this,JAHPKOOJOGP *GKDHBGOOKBH)

{
  undefined2 uVar1;
  undefined *puVar2;
  undefined *puVar3;
  code *pcVar4;
  longlong *plVar5;
  char cVar6;
  longlong lVar7;
  undefined8 uVar8;
  ulonglong uVar9;
  undefined **ppuVar10;
  ulonglong uVar11;
  undefined *puStackX_8;
  
  if (GKDHBGOOKBH == (JAHPKOOJOGP *)0x0) {
    FUN_1804fe400();
    pcVar4 = (code *)swi(3);
    (*pcVar4)();
    return;
  }
  lVar7 = FUN_183487710(GKDHBGOOKBH,_DAT_189a9cc18);
  if (lVar7 == 0) {
    FUN_1804fe400();
    pcVar4 = (code *)swi(3);
    (*pcVar4)();
    return;
  }
  if (*(int *)(lVar7 + 0x10) != 0) {
    return;
  }
  puVar2 = this->NPCKMANPHEJ;
  if (puVar2 == (undefined *)0x0) {
    FUN_1804fe400();
    pcVar4 = (code *)swi(3);
    (*pcVar4)();
    return;
  }
  puStackX_8 = puVar2;
  lVar7 = *(longlong *)(puVar2 + 0x68);
  if (lVar7 == 0) {
    uVar11 = 1;
    ppuVar10 = &puStackX_8;
  }
  else {
    uVar11 = *(ulonglong *)(lVar7 + 0x18);
    ppuVar10 = (undefined **)(lVar7 + 0x20);
  }
  uVar9 = 0;
  if (uVar11 != 0) {
    do {
      puVar3 = ppuVar10[uVar9];
      pcVar4 = *(code **)(puVar3 + 0x10);
      plVar5 = *(longlong **)(puVar3 + 0x20);
      lVar7 = *(longlong *)(puVar3 + 0x28);
      if (*(short *)(lVar7 + 0x30) == -1) {
        thunk_FUN_180448910(lVar7);
      }
      cVar6 = FUN_1804fe050(lVar7);
      if (cVar6 == '\0') {
        if ((((plVar5 == (longlong *)0x0) || (*(short *)(lVar7 + 0x30) == -1)) ||
            ((*(uint *)(*plVar5 + 0x10c) >> 8 & 1) != 0)) || (*(longlong *)(puVar2 + 0x18) == 0))
        goto LAB_186ae44cb;
        cVar6 = thunk_FUN_180442270(lVar7);
        if (cVar6 == '\0') {
          cVar6 = FUN_1804fe3a0(lVar7);
          if (cVar6 == '\0') {
            (**(code **)(*plVar5 + 0x148 + (ulonglong)*(ushort *)(lVar7 + 0x30) * 0x10))
                      (plVar5,*(undefined8 *)
                               (*plVar5 + 0x150 + (ulonglong)*(ushort *)(lVar7 + 0x30) * 0x10));
          }
          else {
            uVar1 = *(undefined2 *)(lVar7 + 0x30);
            uVar8 = thunk_FUN_180432d70(lVar7);
            FUN_180257630(uVar1,uVar8,plVar5);
          }
        }
        else {
          cVar6 = FUN_1804fe3a0(lVar7);
          if (cVar6 == '\0') {
            FUN_180306e50(lVar7,plVar5);
          }
          else {
            FUN_1802ced20();
          }
        }
      }
      else if (*(char *)(lVar7 + 0x32) == '\0') {
        (*pcVar4)(lVar7);
      }
      else {
LAB_186ae44cb:
        (*pcVar4)(plVar5,lVar7);
      }
      uVar9 = uVar9 + 1;
    } while (uVar9 < uVar11);
  }
  return;
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



/* ================= 0x18052E920 ================= */
/* name   = ELHKNLNBGOM */
/* entry  = 18052e920 */
/* body   = 401 bytes */
/* sig    = void ELHKNLNBGOM(DBPLMDDEMML_45307 * this, byte GLKNCBCNDMN) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void DBPLMDDEMML::ELHKNLNBGOM(bool GLKNCBCNDMN)  token=060222EC */

void DBPLMDDEMML::ELHKNLNBGOM(DBPLMDDEMML_45307 *this,byte GLKNCBCNDMN)

{
  longlong lVar1;
  code *pcVar2;
  char cVar3;
  longlong lVar4;
  undefined *puVar5;
  
  if (GLKNCBCNDMN != 0) {
    lVar4 = *_DAT_189a9bde8;
    if (*(char *)(lVar4 + 0x136) == '\0') {
      FUN_18043e4c0(lVar4);
    }
    lVar4 = **(longlong **)(lVar4 + 0x90);
    if (*(char *)(lVar4 + 0x136) == '\0') {
      FUN_18043e4c0(lVar4);
    }
    if ((LHAIOMLEMMM *)**(undefined8 **)(lVar4 + 0x28) == (LHAIOMLEMMM *)0x0) {
      FUN_1804fe400();
      pcVar2 = (code *)swi(3);
      (*pcVar2)();
      return;
    }
    cVar3 = MoleMole::LHAIOMLEMMM::INKCBFBNJDP((LHAIOMLEMMM *)**(undefined8 **)(lVar4 + 0x28));
    if (cVar3 != '\0') {
      lVar4 = *_DAT_189a982e8;
      if (*(char *)(lVar4 + 0x136) == '\0') {
        FUN_18043e4c0(lVar4);
      }
      lVar4 = **(longlong **)(lVar4 + 0x90);
      if (*(char *)(lVar4 + 0x136) == '\0') {
        FUN_18043e4c0(lVar4);
      }
      if ((NotifyManager *)**(undefined8 **)(lVar4 + 0x28) == (NotifyManager *)0x0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      MoleMole::NotifyManager::FireNotify((NotifyManager *)**(undefined8 **)(lVar4 + 0x28));
      lVar4 = thunk_FUN_1804457f0(_DAT_189a15930);
      MoleMole::LoadingWheelWidgetContext::_ctor(lVar4,0xc56,0);
      puVar5 = this->LPCADCIJAEA;
      if (puVar5 == (undefined *)0x0) {
        puVar5 = (undefined *)thunk_FUN_1804457f0(_DAT_189a15430);
        KeyGeneratedEventHandler::_ctor(puVar5,this,_DAT_189a9bdf0,0);
        this->LPCADCIJAEA = puVar5;
      }
      if (lVar4 == 0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      *(undefined **)(lVar4 + 0xc0) = puVar5;
      lVar1 = *_DAT_189a985c0;
      if (*(char *)(lVar1 + 0x136) == '\0') {
        FUN_18043e4c0(lVar1);
      }
      lVar1 = **(longlong **)(lVar1 + 0x90);
      if (*(char *)(lVar1 + 0x136) == '\0') {
        FUN_18043e4c0(lVar1);
      }
      if (**(longlong **)(lVar1 + 0x28) == 0) {
        FUN_1804fe400();
        pcVar2 = (code *)swi(3);
        (*pcVar2)();
        return;
      }
      MoleMole::MainUIManager::ShowWidget(**(longlong **)(lVar1 + 0x28),lVar4,0);
    }
  }
  return;
}



/* ================= 0x18052EAC0 ================= */
/* name   = NKALEOFHPGG */
/* entry  = 18052eac0 */
/* body   = 40 bytes */
/* sig    = byte NKALEOFHPGG(DFGMBKKJIIA_35494 * this, ChapterOWHeroCardMetaData * KOPNFGMFGBF) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: bool DFGMBKKJIIA::NKALEOFHPGG(MoleMole.ExcelMeta.ChapterOWHeroCardMetaData KOPNFGMFGBF)
   token=0600DBCF */

byte DFGMBKKJIIA::NKALEOFHPGG(DFGMBKKJIIA_35494 *this,ChapterOWHeroCardMetaData *KOPNFGMFGBF)

{
  code *pcVar1;
  byte bVar2;
  int iVar3;
  
  if (KOPNFGMFGBF != (ChapterOWHeroCardMetaData *)0x0) {
    iVar3 = MoleMole::ExcelMeta::ChapterOWHeroCardMetaData::get_MapID(KOPNFGMFGBF);
    return iVar3 == this->GCLDJCMKLDI;
  }
  FUN_1804fe400();
  pcVar1 = (code *)swi(3);
  bVar2 = (*pcVar1)();
  return bVar2;
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
  char cVar3;
  int iVar4;
  longlong lVar5;
  undefined8 *puVar6;
  Call CStack_58;
  undefined8 auStack_30 [5];
  
  auStack_30[0] = 0x18052eb0a;
  cVar3 = IFix::WrappersManagerImpl::IsPatched(0x1fb92);
  if (cVar3 != '\0') {
    auStack_30[0] = 0x18052eb87;
    lVar5 = IFix::WrappersManagerImpl::GetPatch(0x1fb92);
    if (lVar5 == 0) {
      auStack_30[0] = 0x18052ebbb;
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
    puVar6 = (undefined8 *)IFix::Core::Call::Begin(auStack_30,this,initiator);
    CStack_58.argumentBase = (undefined *)*puVar6;
    CStack_58.evaluationStackBase = (undefined *)puVar6[1];
    CStack_58.managedStack = (undefined *)puVar6[2];
    CStack_58.currentTop = (undefined *)puVar6[3];
    CStack_58.topWriteBack = (undefined *)puVar6[4];
    if (*(longlong *)(lVar5 + 0x20) != 0) {
      IFix::Core::Call::PushObject(&CStack_58);
    }
    IFix::Core::Call::PushObject(&CStack_58);
    IFix::Core::Call::PushObject(&CStack_58);
    if (*(VirtualMachine **)(lVar5 + 0x10) != (VirtualMachine *)0x0) {
      IFix::Core::VirtualMachine::Execute(*(VirtualMachine **)(lVar5 + 0x10));
      return;
    }
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    (*pcVar2)();
    return;
  }
  if (initiator == (BattlerModel *)0x0) {
    auStack_30[0] = 0x18052ebb5;
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    (*pcVar2)();
    return;
  }
  this->damage = initiator->attack;
  plVar1 = (longlong *)initiator->battler;
  if (plVar1 != (longlong *)0x0) {
    auStack_30[0] = 0x18052eb3a;
    iVar4 = (**(code **)(*plVar1 + 0x278))(plVar1,*(undefined8 *)(*plVar1 + 0x280));
    this->power = iVar4 + 100;
    plVar1 = (longlong *)initiator->battler;
    if (plVar1 != (longlong *)0x0) {
      auStack_30[0] = 0x18052eb59;
      iVar4 = (**(code **)(*plVar1 + 0x288))(plVar1,*(undefined8 *)(*plVar1 + 0x290));
      this->finalConst = 0;
      this->vulnerable = iVar4 + 100;
      this->critRate = initiator->critRate;
      this->critDamage = initiator->critDamage;
      return;
    }
    auStack_30[0] = 0x18052eba9;
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    (*pcVar2)();
    return;
  }
  auStack_30[0] = 0x18052ebaf;
  FUN_1804fe400();
  pcVar2 = (code *)swi(3);
  (*pcVar2)();
  return;
}



/* ================= 0x18052F230 ================= */
/* name   = CreateTileData */
/* entry  = 18052f230 */
/* body   = 198 bytes */
/* sig    = pointer CreateTileData(GEMapDataItem * this, pointer hexCoord) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: MoleMole_GlobalExplore_GETileDataItem
   GEMapDataItem::CreateTileData(MoleMole.GlobalExplore.HexCoord hexCoord)  token=0602FE8D */

undefined *
MoleMole::GlobalExplore::GEMapDataItem::CreateTileData(GEMapDataItem *this,undefined *hexCoord)

{
  code *pcVar1;
  char cVar2;
  undefined *puVar3;
  ILFixDynamicMethodWrapper_57479 *this_00;
  undefined *puStackX_18;
  
  cVar2 = IFix::WrappersManagerImpl::IsPatched(0x28d9b);
  if (cVar2 != '\0') {
    this_00 = (ILFixDynamicMethodWrapper_57479 *)IFix::WrappersManagerImpl::GetPatch(0x28d9b);
    puStackX_18 = hexCoord;
    thunk_FUN_18042cf20(_DAT_189a17480,&puStackX_18);
    if (this_00 != (ILFixDynamicMethodWrapper_57479 *)0x0) {
      puVar3 = (undefined *)IFix::ILFixDynamicMethodWrapper::Gen_Wrap_13140(this_00);
      return puVar3;
    }
    FUN_1804fe400();
    pcVar1 = (code *)swi(3);
    puVar3 = (undefined *)(*pcVar1)();
    return puVar3;
  }
  puVar3 = (undefined *)thunk_FUN_1804457f0(_DAT_189a17488);
  GETileDataItem::_ctor(puVar3,hexCoord);
  if (this->tiles != (undefined *)0x0) {
    FUN_185175830(this->tiles,hexCoord,puVar3,_DAT_189a9b9c0);
    return puVar3;
  }
  FUN_1804fe400();
  pcVar1 = (code *)swi(3);
  puVar3 = (undefined *)(*pcVar1)();
  return puVar3;
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
  code *pcVar2;
  char cVar3;
  uint uVar4;
  longlong lVar5;
  undefined8 *puVar6;
  undefined8 uVar7;
  GEAreaData *pGVar8;
  Call CStack_58;
  undefined8 auStack_30 [5];
  
  auStack_30[0] = 0x18052f809;
  cVar3 = IFix::WrappersManagerImpl::IsPatched(0x9f05);
  if (cVar3 != '\0') {
    auStack_30[0] = 0x18052f860;
    lVar5 = IFix::WrappersManagerImpl::GetPatch(0x9f05);
    if (lVar5 == 0) {
      auStack_30[0] = 0x18052f88e;
      FUN_1804fe400();
      pcVar2 = (code *)swi(3);
      pGVar8 = (GEAreaData *)(*pcVar2)();
      return pGVar8;
    }
    CStack_58.argumentBase = (undefined *)0x0;
    CStack_58.evaluationStackBase = (undefined *)0x0;
    CStack_58.managedStack = (undefined *)0x0;
    CStack_58.currentTop = (undefined *)0x0;
    CStack_58.topWriteBack = (undefined *)0x0;
    puVar6 = (undefined8 *)IFix::Core::Call::Begin(auStack_30,this,areaID);
    CStack_58.argumentBase = (undefined *)*puVar6;
    CStack_58.evaluationStackBase = (undefined *)puVar6[1];
    CStack_58.managedStack = (undefined *)puVar6[2];
    CStack_58.currentTop = (undefined *)puVar6[3];
    CStack_58.topWriteBack = (undefined *)puVar6[4];
    if (*(longlong *)(lVar5 + 0x20) != 0) {
      IFix::Core::Call::PushObject(&CStack_58);
    }
    IFix::Core::Call::PushObject(&CStack_58);
    IFix::Core::Call::PushInt32(&CStack_58);
    if (*(VirtualMachine **)(lVar5 + 0x10) != (VirtualMachine *)0x0) {
      IFix::Core::VirtualMachine::Execute(*(VirtualMachine **)(lVar5 + 0x10));
      pGVar8 = (GEAreaData *)FUN_18347f130(&CStack_58,0,_DAT_189adb1e8);
      return pGVar8;
    }
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    pGVar8 = (GEAreaData *)(*pcVar2)();
    return pGVar8;
  }
  if (this->areaGlobalTiles == (undefined *)0x0) {
    auStack_30[0] = 0x18052f888;
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    pGVar8 = (GEAreaData *)(*pcVar2)();
    return pGVar8;
  }
  auStack_30[0] = 0x18052f824;
  cVar3 = FUN_184d554c0(this->areaGlobalTiles,areaID,_DAT_189a9ba88);
  if (cVar3 == '\0') {
    return (GEAreaData *)0x0;
  }
  puVar1 = this->areaGlobalTiles;
  if (puVar1 == (undefined *)0x0) {
    auStack_30[0] = 0x18052f882;
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    pGVar8 = (GEAreaData *)(*pcVar2)();
    return pGVar8;
  }
  if (puVar1 == (undefined *)0x0) {
    auStack_30[0] = 0x184d75319;
    FUN_1804fe400(0,areaID);
    pcVar2 = (code *)swi(3);
    pGVar8 = (GEAreaData *)(*pcVar2)();
    return pGVar8;
  }
  auStack_30[0] = 0x184d752b4;
  uVar4 = FUN_184d58230(puVar1,areaID,*(undefined8 *)(*(longlong *)(*_DAT_189a9ba90 + 0x90) + 0x88))
  ;
  if ((int)uVar4 < 0) {
    auStack_30[0] = 0x184d752e3;
    uVar7 = thunk_FUN_1804457f0(_DAT_1899e0068);
    auStack_30[0] = 0x184d752ee;
    System::Collections::Generic::KeyNotFoundException::_ctor(uVar7);
    auStack_30[0] = 0x184d752fd;
    FUN_1804fe3d0(uVar7,_DAT_189a6e8c8);
    pcVar2 = (code *)swi(3);
    pGVar8 = (GEAreaData *)(*pcVar2)();
    return pGVar8;
  }
  lVar5 = *(longlong *)(puVar1 + 0x18);
  if (lVar5 != 0) {
    if (uVar4 < *(uint *)(lVar5 + 0x18)) {
      return *(GEAreaData **)(lVar5 + 0x30 + (longlong)(int)uVar4 * 0x18);
    }
    auStack_30[0] = 0x184d75303;
    uVar7 = thunk_FUN_180436120();
    auStack_30[0] = 0x184d7530d;
    FUN_1804fe3d0(uVar7,0);
    pcVar2 = (code *)swi(3);
    pGVar8 = (GEAreaData *)(*pcVar2)();
    return pGVar8;
  }
  auStack_30[0] = 0x184d75313;
  FUN_1804fe400();
  pcVar2 = (code *)swi(3);
  pGVar8 = (GEAreaData *)(*pcVar2)();
  return pGVar8;
}



/* ================= 0x18052F890 ================= */
/* name   = GetCampByID */
/* entry  = 18052f890 */
/* body   = 200 bytes */
/* sig    = GECampData * GetCampByID(GEMapDataItem * this, int campID) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: MoleMole_GlobalExplore_GECampData GEMapDataItem::GetCampByID(int campID)  token=0602FE96 */

GECampData * MoleMole::GlobalExplore::GEMapDataItem::GetCampByID(GEMapDataItem *this,int campID)

{
  undefined *puVar1;
  longlong lVar2;
  code *pcVar3;
  longlong *plVar4;
  char cVar5;
  SoapFieldAttribute *this_00;
  longlong lVar6;
  undefined8 *puVar7;
  undefined8 uVar8;
  GECampData *pGVar9;
  uint uVar10;
  Call CStack_58;
  undefined8 auStack_30 [5];
  
  auStack_30[0] = 0x18052f8a9;
  cVar5 = IFix::WrappersManagerImpl::IsPatched(0x28dd9);
  if (cVar5 != '\0') {
    auStack_30[0] = 0x18052f929;
    lVar6 = IFix::WrappersManagerImpl::GetPatch(0x28dd9);
    if (lVar6 == 0) {
      auStack_30[0] = 0x18052f957;
      FUN_1804fe400();
      pcVar3 = (code *)swi(3);
      pGVar9 = (GECampData *)(*pcVar3)();
      return pGVar9;
    }
    CStack_58.argumentBase = (undefined *)0x0;
    CStack_58.evaluationStackBase = (undefined *)0x0;
    CStack_58.managedStack = (undefined *)0x0;
    CStack_58.currentTop = (undefined *)0x0;
    CStack_58.topWriteBack = (undefined *)0x0;
    puVar7 = (undefined8 *)IFix::Core::Call::Begin(auStack_30,this,campID);
    CStack_58.argumentBase = (undefined *)*puVar7;
    CStack_58.evaluationStackBase = (undefined *)puVar7[1];
    CStack_58.managedStack = (undefined *)puVar7[2];
    CStack_58.currentTop = (undefined *)puVar7[3];
    CStack_58.topWriteBack = (undefined *)puVar7[4];
    if (*(longlong *)(lVar6 + 0x20) != 0) {
      IFix::Core::Call::PushObject(&CStack_58);
    }
    IFix::Core::Call::PushObject(&CStack_58);
    IFix::Core::Call::PushInt32(&CStack_58);
    if (*(VirtualMachine **)(lVar6 + 0x10) == (VirtualMachine *)0x0) {
      FUN_1804fe400();
      pcVar3 = (code *)swi(3);
      pGVar9 = (GECampData *)(*pcVar3)();
      return pGVar9;
    }
    IFix::Core::VirtualMachine::Execute(*(VirtualMachine **)(lVar6 + 0x10));
    pGVar9 = (GECampData *)FUN_18347f130(&CStack_58,0,_DAT_189adb1d8);
    return pGVar9;
  }
  auStack_30[0] = 0x18052f8be;
  this_00 = (SoapFieldAttribute *)thunk_FUN_1804457f0(_DAT_189a17498);
  auStack_30[0] = 0x18052f8c9;
  Mono::Xml::SecurityParser::probe_1826b9250(this_00);
  if (this_00 == (SoapFieldAttribute *)0x0) {
    auStack_30[0] = 0x18052f951;
    FUN_1804fe400();
    pcVar3 = (code *)swi(3);
    pGVar9 = (GECampData *)(*pcVar3)();
    return pGVar9;
  }
  this_00->useAttribute = (char)campID;
  this_00->pad_11[0] = (char)((uint)campID >> 8);
  this_00->pad_11[1] = (char)((uint)campID >> 0x10);
  this_00->pad_11[2] = (char)((uint)campID >> 0x18);
  puVar1 = this->camps;
  auStack_30[0] = 0x18052f8e1;
  lVar6 = thunk_FUN_1804457f0(_DAT_189a174a0);
  auStack_30[0] = 0x18052f8f9;
  KeyGeneratedEventHandler::_ctor(lVar6,this_00,_DAT_189a9ba98,0);
  plVar4 = _DAT_189a9baa0;
  if (puVar1 == (undefined *)0x0) {
    auStack_30[0] = 0x18052f94b;
    FUN_1804fe400();
    pcVar3 = (code *)swi(3);
    pGVar9 = (GECampData *)(*pcVar3)();
    return pGVar9;
  }
  if (lVar6 == 0) {
    auStack_30[0] = 0x184ca134b;
    System::ThrowHelper::ThrowArgumentNullException(8);
  }
  uVar10 = 0;
  if (0 < *(int *)(puVar1 + 0x18)) {
    do {
      lVar2 = *(longlong *)(puVar1 + 0x10);
      if (lVar2 == 0) {
        auStack_30[0] = 0x184ca13f6;
        FUN_1804fe400();
        pcVar3 = (code *)swi(3);
        pGVar9 = (GECampData *)(*pcVar3)();
        return pGVar9;
      }
      if (*(uint *)(lVar2 + 0x18) <= uVar10) {
        auStack_30[0] = 0x184ca13e6;
        uVar8 = thunk_FUN_180436120();
        auStack_30[0] = 0x184ca13f0;
        FUN_1804fe3d0(uVar8,0);
        pcVar3 = (code *)swi(3);
        pGVar9 = (GECampData *)(*pcVar3)();
        return pGVar9;
      }
      if (lVar6 == 0) {
        auStack_30[0] = 0x184ca13e0;
        FUN_1804fe400();
        pcVar3 = (code *)swi(3);
        pGVar9 = (GECampData *)(*pcVar3)();
        return pGVar9;
      }
      auStack_30[0] = 0x184ca138a;
      cVar5 = InitDelegate::Invoke
                        (lVar6,*(undefined8 *)(lVar2 + 0x20 + (longlong)(int)uVar10 * 8),
                         *(undefined8 *)(*(longlong *)(*plVar4 + 0x90) + 0xd0));
      if (cVar5 != '\0') {
        lVar6 = *(longlong *)(puVar1 + 0x10);
        if (lVar6 == 0) {
          auStack_30[0] = 0x184ca13da;
          FUN_1804fe400();
          pcVar3 = (code *)swi(3);
          pGVar9 = (GECampData *)(*pcVar3)();
          return pGVar9;
        }
        if (uVar10 < *(uint *)(lVar6 + 0x18)) {
          return *(GECampData **)(lVar6 + 0x20 + (longlong)(int)uVar10 * 8);
        }
        auStack_30[0] = 0x184ca13ca;
        uVar8 = thunk_FUN_180436120();
        auStack_30[0] = 0x184ca13d4;
        FUN_1804fe3d0(uVar8,0);
        pcVar3 = (code *)swi(3);
        pGVar9 = (GECampData *)(*pcVar3)();
        return pGVar9;
      }
      uVar10 = uVar10 + 1;
    } while ((int)uVar10 < *(int *)(puVar1 + 0x18));
  }
  return (GECampData *)0x0;
}



/* ================= 0x180530190 ================= */
/* name   = GetTileDataByEntityID */
/* entry  = 180530190 */
/* body   = 415 bytes */
/* sig    = pointer GetTileDataByEntityID(GEMapDataItem * this, int entityID) */


/* WARNING: Removing unreachable block (ram,0x0001805302d5) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: MoleMole_GlobalExplore_GETileDataItem GEMapDataItem::GetTileDataByEntityID(int entityID)
   token=0602FE94 */

undefined *
MoleMole::GlobalExplore::GEMapDataItem::GetTileDataByEntityID(GEMapDataItem *this,int entityID)

{
  code *pcVar1;
  undefined *puVar2;
  char cVar3;
  uint uVar4;
  longlong lVar5;
  undefined8 *puVar6;
  undefined *puVar7;
  ILFixDynamicMethodWrapper_57479 *this_00;
  int aiStack_88 [4];
  undefined8 uStack_78;
  int *piStack_68;
  undefined4 uStack_60;
  undefined *puStack_58;
  undefined *puStack_50;
  undefined *puStack_48;
  undefined1 auStack_40 [24];
  
  uStack_78 = 0xfffffffffffffffe;
  puStack_58 = (undefined *)0x0;
  puStack_50 = (undefined *)0x0;
  puStack_48 = (undefined *)0x0;
  puVar7 = (undefined *)0x0;
  piStack_68 = aiStack_88;
  uStack_60 = 0xffffffff;
  cVar3 = IFix::WrappersManagerImpl::IsPatched(0x28de3);
  if (cVar3 == '\0') {
    if (this->tiles == (undefined *)0x0) {
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      puVar7 = (undefined *)(*pcVar1)();
      return puVar7;
    }
    lVar5 = FUN_185184260(this->tiles,_DAT_189a9ba78);
    if (lVar5 == 0) {
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      puVar7 = (undefined *)(*pcVar1)();
      return puVar7;
    }
    puVar6 = (undefined8 *)FUN_184e8bec0(auStack_40,lVar5,_DAT_189a9ba80);
    puStack_58 = (undefined *)*puVar6;
    puStack_50 = (undefined *)puVar6[1];
    puStack_48 = (undefined *)puVar6[2];
    do {
      cVar3 = FUN_1848a8f80(&puStack_58,0);
      puVar2 = puStack_48;
      if (cVar3 == '\0') {
LAB_18053029e:
        aiStack_88[0] = 0x71;
        goto LAB_1805302c5;
      }
      if (puStack_48 == (undefined *)0x0) {
        FUN_1804fe400();
        goto LAB_18053029e;
      }
    } while ((*(GEEntityDataItem **)(puStack_48 + 0x18) == (GEEntityDataItem *)0x0) ||
            (uVar4 = GEEntityDataItem::get_EntityID(*(GEEntityDataItem **)(puStack_48 + 0x18)),
            (ulonglong)uVar4 != (longlong)entityID));
    aiStack_88[0] = 0x73;
    puVar7 = puVar2;
LAB_1805302c5:
    uStack_60 = 0;
    Mono::Xml::SecurityParser::OnStartParsing((SoapFieldAttribute *)&puStack_58);
    if (aiStack_88[0] != 0x73) {
      puVar7 = (undefined *)0x0;
    }
  }
  else {
    this_00 = (ILFixDynamicMethodWrapper_57479 *)IFix::WrappersManagerImpl::GetPatch(0x28de3);
    if (this_00 == (ILFixDynamicMethodWrapper_57479 *)0x0) {
      FUN_1804fe400();
      pcVar1 = (code *)swi(3);
      puVar7 = (undefined *)(*pcVar1)();
      return puVar7;
    }
    puVar7 = (undefined *)IFix::ILFixDynamicMethodWrapper::Gen_Wrap_13190(this_00);
  }
  return puVar7;
}



