1821D7BE0	
DateTime *d2;
undefined *object;
MainUIManager *this_00;
double dVar1;
bool bVar2;
byte bVar3;
Transform *pTVar4;
longlong lVar5;
BasePageContext *currentPage;
BaseContext *pBVar6;
Transform *pTVar7;
DateTime *d1;
MiHoYoGameData *this_01;
DKCCFNENGLA *this_02;
MainPageContext *this_03;
ILFixDynamicMethodWrapper *pIVar8;
undefined *puVar9;
KeyGeneratedEventHandler *pKVar10;
undefined8 uVar11;
IntegratedReturneeDialogContext *this_04;
Call *pCVar12;
float fVar13;
TimeSpan *pTStackX_20;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1821d7bf3;
bVar3 = IFix::WrappersManagerImpl::IsPatched(0x1d2d9);
if (bVar3 != 0) {
  uStack_30 = 0x1821d7c20;
  pIVar8 = IFix::WrappersManagerImpl::GetPatch(0x1d2d9);
  if (pIVar8 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1821d7c3a;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar12 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar12->argumentBase;
  CStack_58.evaluationStackBase = pCVar12->evaluationStackBase;
  CStack_58.managedStack = pCVar12->managedStack;
  CStack_58.currentTop = pCVar12->currentTop;
  CStack_58.topWriteBack = pCVar12->topWriteBack;
  if (pIVar8->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar8->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar8->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar8->virtualMachine,pIVar8->methodId,&CStack_58,
             (pIVar8->anonObj != (undefined *)0x0) + 1,0);
  return;
}
if (*(int *)(_DAT_189a1c690 + 0xe8) == 0) {
  uStack_30 = 0x1821d7c0c;
  il2cpp::codegen::runtime_class_init();
}
uStack_30 = 0x1819485de;
bVar3 = IFix::WrappersManagerImpl::IsPatched(0x183be);
if (bVar3 != 0) {
  uStack_30 = 0x1819487ca;
  pIVar8 = IFix::WrappersManagerImpl::GetPatch(0x183be);
  if (pIVar8 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1819487e6;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar12 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar12->argumentBase;
  CStack_58.evaluationStackBase = pCVar12->evaluationStackBase;
  CStack_58.managedStack = pCVar12->managedStack;
  CStack_58.currentTop = pCVar12->currentTop;
  CStack_58.topWriteBack = pCVar12->topWriteBack;
  if (pIVar8->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar8->anonObj);
  }
  if ((VirtualMachine *)pIVar8->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar8->virtualMachine,pIVar8->methodId,&CStack_58,
             (uint)(pIVar8->anonObj != (undefined *)0x0),0);
  return;
}
if (*(int *)(_DAT_1899f43a8 + 0xe8) == 0) {
  uStack_30 = 0x18194860a;
  il2cpp::codegen::runtime_class_init();
}
uStack_30 = 0x18194860f;
puVar9 = ExcelMeta::JPPHNBLBABK::IOHFIKFHOML();
if (*(int *)(_DAT_189a1bad8 + 0xe8) == 0) {
  uStack_30 = 0x18194862a;
  il2cpp::codegen::runtime_class_init(_DAT_189a1bad8);
}
pKVar10 = *(KeyGeneratedEventHandler **)(*(longlong *)(_DAT_189a1bad8 + 0x28) + 8);
if (pKVar10 == (KeyGeneratedEventHandler *)0x0) {
  if (*(int *)(_DAT_189a1bad8 + 0xe8) == 0) {
    uStack_30 = 0x18194864e;
    il2cpp::codegen::runtime_class_init(_DAT_189a1bad8);
  }
  object = (undefined *)**(undefined8 **)(_DAT_189a1bad8 + 0x28);
  uStack_30 = 0x181948668;
  pKVar10 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_189a44250);
  uStack_30 = 0x181948680;
  KeyGeneratedEventHandler::_ctor(pKVar10,object,_DAT_189b02060);
  *(KeyGeneratedEventHandler **)(*(longlong *)(_DAT_189a1bad8 + 0x28) + 8) = pKVar10;
}
uStack_30 = 0x1819486a1;
uVar11 = FUN_183ab8c00(puVar9,pKVar10,_DAT_189b02068);
if (*(int *)(_DAT_189a1bad8 + 0xe8) == 0) {
  uStack_30 = 0x1819486bc;
  il2cpp::codegen::runtime_class_init(_DAT_189a1bad8);
}
pKVar10 = *(KeyGeneratedEventHandler **)(*(longlong *)(_DAT_189a1bad8 + 0x28) + 0x10);
if (pKVar10 == (KeyGeneratedEventHandler *)0x0) {
  if (*(int *)(_DAT_189a1bad8 + 0xe8) == 0) {
    uStack_30 = 0x1819486e0;
    il2cpp::codegen::runtime_class_init(_DAT_189a1bad8);
  }
  puVar9 = (undefined *)**(undefined8 **)(_DAT_189a1bad8 + 0x28);
  uStack_30 = 0x1819486fa;
  pKVar10 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_189a44258);
  uStack_30 = 0x181948712;
  KeyGeneratedEventHandler::_ctor(pKVar10,puVar9,_DAT_189b02070);
  *(KeyGeneratedEventHandler **)(*(longlong *)(_DAT_189a1bad8 + 0x28) + 0x10) = pKVar10;
}
uStack_30 = 0x181948733;
uVar11 = FUN_1813a6500(uVar11,pKVar10);
uStack_30 = 0x18194873d;
puVar9 = (undefined *)FUN_1813aac10(uVar11,0);
lVar5 = *_DAT_189a985c0;
if (*(char *)(lVar5 + 0x136) == '\0') {
  uStack_30 = 0x18194875b;
  FUN_18043e4c0(lVar5);
}
lVar5 = **(longlong **)(lVar5 + 0x90);
if (*(char *)(lVar5 + 0x136) == '\0') {
  uStack_30 = 0x181948776;
  FUN_18043e4c0(lVar5);
}
this_00 = (MainUIManager *)**(undefined8 **)(lVar5 + 0x28);
uStack_30 = 0x181948789;
this_04 = (IntegratedReturneeDialogContext *)il2cpp::codegen::object_new(_DAT_189a1c690);
uStack_30 = 0x18194879a;
IntegratedReturneeDialogContext::_ctor(this_04,puVar9,(Action *)0x0);
if (this_00 == (MainUIManager *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1819487e0;
  il2cpp::codegen::raise_null_reference_exception();
}
pTStackX_20 = (TimeSpan *)0x0;
CStack_58.evaluationStackBase = (undefined *)0x180926c53;
bVar3 = IFix::WrappersManagerImpl::IsPatched(0x70f);
if (bVar3 != 0) {
  CStack_58.evaluationStackBase = (undefined *)0x180926f26;
  pIVar8 = IFix::WrappersManagerImpl::GetPatch(0x70f);
  if (pIVar8 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.evaluationStackBase = (undefined *)0x180926f8c;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.evaluationStackBase = (undefined *)0x180926f3c;
  IFix::ILFixDynamicMethodWrapper::Gen_Wrap_16
            ((ILFixDynamicMethodWrapper_57479 *)pIVar8,(undefined *)this_00,(undefined *)this_04,0
            );
  return;
}
if (this_04 == (IntegratedReturneeDialogContext *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f86;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x180926c6c;
bVar3 = BaseContext::CheckResReady((BaseContext *)this_04);
if (bVar3 == 0) {
  return;
}
CStack_58.evaluationStackBase = (undefined *)0x180926c7f;
bVar3 = UnityEngine::Object::CompareBaseObjects
                  ((Object *)this_00->SceneCanvas_k_BackingField,(Object *)0x0);
if (bVar3 != 0) {
  return;
}
CStack_58.evaluationStackBase = (undefined *)0x180926c9e;
pTVar4 = MainUIManager::GetUIHolder(this_00,this_04->uiType);
if (this_00->pageContextStack == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f80;
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(int *)(this_00->pageContextStack + 0x18) < 1) {
  CStack_58.evaluationStackBase = (undefined *)0x180926cc4;
  lVar5 = func_0x000180257760(this_00->SceneCanvas_k_BackingField,_DAT_189a157f0);
  if (lVar5 != 0) {
    CStack_58.evaluationStackBase = (undefined *)0x180926cd1;
    bVar3 = MainUIManager::HasContextInStash(this_00);
    if (bVar3 != 0) {
      CStack_58.evaluationStackBase = (undefined *)0x180926cdd;
      MainUIManager::RecoveryPageStackFromStashOnly(this_00);
    }
  }
}
puVar9 = this_00->pageContextStack;
if (puVar9 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f7a;
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(int *)(puVar9 + 0x18) < 1) {
  CStack_58.evaluationStackBase = (undefined *)0x180926d05;
  lVar5 = func_0x000180257760(this_00->SceneCanvas_k_BackingField,_DAT_189a157f0);
  if (lVar5 == 0) {
    currentPage = (BasePageContext *)this_00->emptyPageContext;
    if (currentPage != (BasePageContext *)0x0) goto LAB_180926d4f;
  }
  else {
    CStack_58.evaluationStackBase = (undefined *)0x180926ef5;
    this_03 = (MainPageContext *)il2cpp::codegen::object_new(_DAT_189a16920);
    CStack_58.evaluationStackBase = (undefined *)0x180926f00;
    MainPageContext::_ctor(this_03);
    if (puVar9 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.evaluationStackBase = (undefined *)0x180926f4a;
      il2cpp::codegen::raise_null_reference_exception();
    }
    CStack_58.evaluationStackBase = (undefined *)0x180926f17;
    FUN_185585c90(puVar9,this_03);
  }
}
puVar9 = this_00->pageContextStack;
if (puVar9 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f74;
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(int *)(puVar9 + 0x18) < 1) {
  return;
}
if (puVar9 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f6e;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x180926d43;
currentPage = (BasePageContext *)FUN_185585a70(puVar9,_DAT_189ab5e90);
if (currentPage == (BasePageContext *)0x0) {
  return;
}
LAB_180926d4f:
CStack_58.evaluationStackBase = (undefined *)0x180926d5a;
pBVar6 = MainUIManager::GetTheLastContext(this_00,currentPage);
CStack_58.evaluationStackBase = (undefined *)0x180926d6b;
MainUIManager::HandleTopContextParticleNodesActive(this_00,currentPage,0);
if (currentPage == (BasePageContext *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f68;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x180926d7f;
BasePageContext::AddDialog(currentPage,(BaseDialogContext *)this_04);
if (pBVar6 != (BaseContext *)0x0) {
  CStack_58.evaluationStackBase = (undefined *)0x180926d98;
  (**(code **)(pBVar6->__klass + 0x308))(pBVar6,*(undefined8 *)(pBVar6->__klass + 0x310));
}
this_04->pageContext = (undefined *)currentPage;
if ((Component *)this_00->SceneCanvas_k_BackingField == (Component *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f62;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x180926db1;
pTVar7 = UnityEngine::Component::get_transform((Component *)this_00->SceneCanvas_k_BackingField);
CStack_58.evaluationStackBase = (undefined *)0x180926dcb;
(**(code **)(this_04->__klass + 0x188))
          (this_04,pTVar7,pTVar4,*(undefined8 *)(this_04->__klass + 400));
CStack_58.evaluationStackBase = (undefined *)0x180926dd9;
MainUIManager::HandleTopContextParticleNodesActive(this_00,currentPage,1);
bVar2 = false;
if ((char)(this_00->lastTimeToReportPlayerSpendTimeData).TicksPerSecond != '\0') {
  if (*(int *)(_DAT_189a15420 + 0xe8) == 0) {
    CStack_58.evaluationStackBase = (undefined *)0x180926dff;
    il2cpp::codegen::runtime_class_init();
  }
  CStack_58.evaluationStackBase = (undefined *)0x180926e04;
  d1 = TimeUtil::get_NowDateTime();
  d2 = (DateTime *)(this_00->lastTimeToReportPlayerSpendTimeData).TicksPerMillisecond;
  if (*(int *)(_DAT_1899de528 + 0xe8) == 0) {
    CStack_58.evaluationStackBase = (undefined *)0x180926e20;
    il2cpp::codegen::runtime_class_init();
  }
  CStack_58.evaluationStackBase = (undefined *)0x180926e2b;
  pTStackX_20 = System::DateTime::op_Subtraction(d1,d2);
  CStack_58.evaluationStackBase = (undefined *)0x180926e3a;
  dVar1 = System::TimeSpan::get_TotalSeconds((TimeSpan *)&pTStackX_20);
  if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
    CStack_58.evaluationStackBase = (undefined *)0x180926e52;
    il2cpp::codegen::runtime_class_init();
  }
  CStack_58.evaluationStackBase = (undefined *)0x180926e57;
  fVar13 = ExcelMeta::ConstValueDataReaderExtend::get_CDTimeToReportPlayerSpeedTimeData();
  bVar2 = (double)fVar13 < dVar1;
  if ((double)fVar13 < dVar1) {
    CStack_58.evaluationStackBase = (undefined *)0x180926e7a;
    this_01 = (MiHoYoGameData *)FUN_180261460(_DAT_189a98398);
    if (this_01 == (MiHoYoGameData *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.evaluationStackBase = (undefined *)0x180926f56;
      il2cpp::codegen::raise_null_reference_exception();
    }
    CStack_58.evaluationStackBase = (undefined *)0x180926e8b;
    this_02 = MiHoYoGameData::get_LocalData(this_01);
    if (this_02 == (DKCCFNENGLA *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.evaluationStackBase = (undefined *)0x180926f50;
      il2cpp::codegen::raise_null_reference_exception();
    }
    CStack_58.evaluationStackBase = (undefined *)0x180926e9e;
    DKCCFNENGLA::ONHMNAIAFML(this_02,0);
  }
}
CStack_58.evaluationStackBase = (undefined *)0x180926ea9;
MainUIManager::RecordShowContext(this_00,(BaseContext *)this_04);
if (bVar2) {
  CStack_58.evaluationStackBase = (undefined *)0x180926eb7;
  MainUIManager::TryToSendPlayerSpendTimeDataToServer(this_00,0);
}
if ((AsyncCallback *)this_00->OnDialogShow != (AsyncCallback *)0x0) {
  if (this_04->config == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.evaluationStackBase = (undefined *)0x180926f5c;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.evaluationStackBase = (undefined *)0x180926ed6;
  System::AsyncCallback::Invoke
            ((AsyncCallback *)this_00->OnDialogShow,*(undefined **)(this_04->config + 0x10));
}
return;\
