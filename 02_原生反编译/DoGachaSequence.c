
uint gachaType;
int boxType;
longlong lVar1;
byte bVar2;
ILFixDynamicMethodWrapper *pIVar3;
Call *pCVar4;
CJPKGNKMFON *pCVar5;
undefined *puVar6;
GachaSequencePageContext *this;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x18528b183;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x18421);
if (bVar2 != 0) {
  uStack_30 = 0x18528b353;
  pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x18421);
  if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18528b38c;
    il2cpp::codegen::raise_null_reference_exception();
  }
IFix_ILFixDynamicMethodWrapper_Gen_Wrap_359:
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar4 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar4->argumentBase;
  CStack_58.evaluationStackBase = pCVar4->evaluationStackBase;
  CStack_58.managedStack = pCVar4->managedStack;
  CStack_58.currentTop = pCVar4->currentTop;
  CStack_58.topWriteBack = pCVar4->topWriteBack;
  if (pIVar3->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar3->anonObj);
  }
  IFix::Core::Call::PushBoolean(&CStack_58,skipBox);
  if ((VirtualMachine *)pIVar3->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar3->virtualMachine,pIVar3->methodId,&CStack_58,
             (pIVar3->anonObj != (undefined *)0x0) + 1,0);
  return;
}
if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
  uStack_30 = 0x18528b1a0;
  il2cpp::codegen::runtime_class_init();
}
uStack_30 = 0x18528b1a5;
bVar2 = ExcelMeta::ConstValueDataReaderExtend::get_IsNewGachaBoxOpen();
if (bVar2 == 0) {
  if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
    uStack_30 = 0x18528b1be;
    il2cpp::codegen::runtime_class_init();
  }
  uStack_30 = 0x18528b5b3;
  bVar2 = IFix::WrappersManagerImpl::IsPatched(0x18424);
  if (bVar2 != 0) {
    uStack_30 = 0x18528b678;
    pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x18424);
    if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x18528b699;
      il2cpp::codegen::raise_null_reference_exception();
    }
    goto IFix_ILFixDynamicMethodWrapper_Gen_Wrap_359;
  }
  lVar1 = *_DAT_189a99f00;
  if (*(char *)(lVar1 + 0x136) == '\0') {
    uStack_30 = 0x18528b5db;
    FUN_18043e4c0(lVar1);
  }
  lVar1 = **(longlong **)(lVar1 + 0x90);
  if (*(char *)(lVar1 + 0x136) == '\0') {
    uStack_30 = 0x18528b5f6;
    FUN_18043e4c0(lVar1);
  }
  if ((JGPPIJBHALG *)**(undefined8 **)(lVar1 + 0x28) == (JGPPIJBHALG *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18528b693;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x18528b610;
  bVar2 = JGPPIJBHALG::GDMMAPCDNJF((JGPPIJBHALG *)**(undefined8 **)(lVar1 + 0x28));
  if ((bVar2 == 0) && (skipBox == 0)) {
    if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
      uStack_30 = 0x18528b62e;
      il2cpp::codegen::runtime_class_init();
    }
    uStack_30 = 0x18528b633;
    TriggerStageGachaBox();
  }
  else {
    if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
      uStack_30 = 0x18528b64a;
      il2cpp::codegen::runtime_class_init();
    }
    uStack_30 = 0x18528b64f;
    ShowGachaDropAnimationAndResultPage();
  }
  if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
    uStack_30 = 0x18528b664;
    il2cpp::codegen::runtime_class_init();
  }
}
else {
  lVar1 = *_DAT_189a9b3d8;
  if (*(char *)(lVar1 + 0x136) == '\0') {
    uStack_30 = 0x18528b1ec;
    FUN_18043e4c0(lVar1);
  }
  lVar1 = **(longlong **)(lVar1 + 0x90);
  if (*(char *)(lVar1 + 0x136) == '\0') {
    uStack_30 = 0x18528b207;
    FUN_18043e4c0(lVar1);
  }
  if ((HCHDIBFGCAL *)**(undefined8 **)(lVar1 + 0x28) == (HCHDIBFGCAL *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18528b386;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x18528b21c;
  pCVar5 = HCHDIBFGCAL::PGKJBDNDLPN((HCHDIBFGCAL *)**(undefined8 **)(lVar1 + 0x28));
  if (pCVar5 == (CJPKGNKMFON *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18528b380;
    il2cpp::codegen::raise_null_reference_exception();
  }
  gachaType = pCVar5->NIBNPDHPGKH;
  boxType = pCVar5->ONOFHKBIOGJ;
  lVar1 = *_DAT_189a9b3d8;
  if (*(char *)(lVar1 + 0x136) == '\0') {
    uStack_30 = 0x18528b251;
    FUN_18043e4c0(lVar1);
  }
  lVar1 = **(longlong **)(lVar1 + 0x90);
  if (*(char *)(lVar1 + 0x136) == '\0') {
    uStack_30 = 0x18528b26c;
    FUN_18043e4c0(lVar1);
  }
  if ((HCHDIBFGCAL *)**(undefined8 **)(lVar1 + 0x28) == (HCHDIBFGCAL *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18528b37a;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x18528b286;
  puVar6 = HCHDIBFGCAL::JECIFOHCFHP((HCHDIBFGCAL *)**(undefined8 **)(lVar1 + 0x28));
  uStack_30 = 0x18528b295;
  this = (GachaSequencePageContext *)il2cpp::codegen::object_new(_DAT_189a2b450);
  uStack_30 = 0x18528b2a4;
  GachaSequencePageContext::_ctor(this,skipBox);
  if (this == (GachaSequencePageContext *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18528b374;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x18528b2b8;
  GachaSequencePageContext::SetResultItems(this,puVar6);
  uStack_30 = 0x18528b2c6;
  GachaSequencePageContext::SetBoxType(this,boxType,gachaType);
  lVar1 = *_DAT_189a985c0;
  if (*(char *)(lVar1 + 0x136) == '\0') {
    uStack_30 = 0x18528b2e1;
    FUN_18043e4c0(lVar1);
  }
  lVar1 = **(longlong **)(lVar1 + 0x90);
  if (*(char *)(lVar1 + 0x136) == '\0') {
    uStack_30 = 0x18528b2fc;
    FUN_18043e4c0(lVar1);
  }
  if ((MainUIManager *)**(undefined8 **)(lVar1 + 0x28) == (MainUIManager *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18528b36e;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x18528b316;
  MainUIManager::ShowPage
            ((MainUIManager *)**(undefined8 **)(lVar1 + 0x28),(BasePageContext *)this,1);
  if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
    uStack_30 = 0x18528b32b;
    il2cpp::codegen::runtime_class_init();
  }
}
uStack_30 = 0x1852957ee;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x18422);
if (bVar2 != 0) {
  uStack_30 = 0x185295831;
  pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x18422);
  if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18529584d;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar4 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar4->argumentBase;
  CStack_58.evaluationStackBase = pCVar4->evaluationStackBase;
  CStack_58.managedStack = pCVar4->managedStack;
  CStack_58.currentTop = pCVar4->currentTop;
  CStack_58.topWriteBack = pCVar4->topWriteBack;
  if (pIVar3->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar3->anonObj);
  }
  if ((VirtualMachine *)pIVar3->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar3->virtualMachine,pIVar3->methodId,&CStack_58,
             (uint)(pIVar3->anonObj != (undefined *)0x0),0);
  return;
}
if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
  uStack_30 = 0x18529580a;
  il2cpp::codegen::runtime_class_init(_DAT_189a15438);
}
puVar6 = *(undefined **)(*(longlong *)(_DAT_189a15438 + 0x28) + 0x70);
if (puVar6 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x185295847;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x183544123;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x18423);
if (bVar2 == 0) {
  if (puVar6[0x10] != '\0') {
    puVar6[0x10] = 0;
  }
  return;
}
uStack_30 = 0x18354413f;
pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x18423);
if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x183544159;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.argumentBase = (undefined *)0x0;
CStack_58.evaluationStackBase = (undefined *)0x0;
CStack_58.managedStack = (undefined *)0x0;
CStack_58.currentTop = (undefined *)0x0;
CStack_58.topWriteBack = (undefined *)0x0;
pCVar4 = IFix::Core::Call::Begin();
CStack_58.argumentBase = pCVar4->argumentBase;
CStack_58.evaluationStackBase = pCVar4->evaluationStackBase;
CStack_58.managedStack = pCVar4->managedStack;
CStack_58.currentTop = pCVar4->currentTop;
CStack_58.topWriteBack = pCVar4->topWriteBack;
if (pIVar3->anonObj != (undefined *)0x0) {
  IFix::Core::Call::PushObject(&CStack_58,pIVar3->anonObj);
}
IFix::Core::Call::PushObject(&CStack_58,puVar6);
if ((VirtualMachine *)pIVar3->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
IFix::Core::VirtualMachine::Execute
          ((VirtualMachine *)pIVar3->virtualMachine,pIVar3->methodId,&CStack_58,
           (pIVar3->anonObj != (undefined *)0x0) + 1,0);
return;\