longlong lVar1;
byte bVar2;
uint uVar3;
OWEndlessModule *pOVar4;
ConfigOWEndless *pCVar5;
ILFixDynamicMethodWrapper *pIVar6;
EndlessBaseData *pEVar7;
OWEndlessDataMode *this_00;
Call *pCVar8;
Call CStack_58;
undefined8 uStack_30;
uStack_30 = 0x18185af13;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x1edc9);
if (bVar2 != 0) {
  uStack_30 = 0x18185b088;
  pIVar6 = IFix::WrappersManagerImpl::GetPatch(0x1edc9);
  if (pIVar6 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */    uStack_30 = 0x18185b0c6;
    il2cpp::codegen::raise_null_reference_exception();
  }
code_r0x000183b83b70:  CStack_58.argumentBase = (undefined *)0x0;
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
  if (pIVar6->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar6->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar6->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute              ((VirtualMachine *)pIVar6->virtualMachine,pIVar6->methodId,&CStack_58,               (pIVar6->anonObj != (undefined *)0x0) + 1,0);
    return;
  }
                  /* WARNING: Subroutine does not return */  il2cpp::codegen::raise_null_reference_exception();
}
if (*(char *)&this->ownerPage == '\0') {
  uStack_30 = 0x18185af38;
  (**(code **)(this->__klass + 0x2b8))(this,*(undefined8 *)(this->__klass + 0x2c0));
  *(undefined1 *)&this->ownerPage = 1;
}
uStack_30 = 0x18185af4f;
(**(code **)(this->__klass + 0x388))(this,*(undefined8 *)(this->__klass + 0x390));
lVar1 = *_DAT_189a981a8;
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x18185af6a;
  FUN_18043e4c0(lVar1);
}
lVar1 = **(longlong **)(lVar1 + 0x90);
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x18185af85;
  FUN_18043e4c0(lVar1);
}
if ((NetworkManager *)**(undefined8 **)(lVar1 + 0x28) == (NetworkManager *)0x0) {
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185b0c0;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x18185af9a;
NetworkManager::RequestOWEndlessData((NetworkManager *)**(undefined8 **)(lVar1 + 0x28));
uStack_30 = 0x18185afa4;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x1edca);
if (bVar2 == 0) {
  if ((OWEndlessInvadeSuccDialogContext *)this->TEXT_ID_LEVEL_REWARD_DIALOG_TITLE !=      (OWEndlessInvadeSuccDialogContext *)0x0) {
    uStack_30 = 0x18185afb6;
    OWEndlessInvadeSuccDialogContext::Close              ((OWEndlessInvadeSuccDialogContext *)this->TEXT_ID_LEVEL_REWARD_DIALOG_TITLE);
    this->TEXT_ID_LEVEL_REWARD_DIALOG_TITLE = (undefined *)0x0;
  }
}
else {
  uStack_30 = 0x18185afca;
  pIVar6 = IFix::WrappersManagerImpl::GetPatch(0x1edca);
  if (pIVar6 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */    uStack_30 = 0x18185b0ba;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x18185afde;
  IFix::ILFixDynamicMethodWrapper::Gen_Wrap_13(pIVar6,(undefined *)this);
}
lVar1 = *_DAT_189a9c530;
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x18185aff9;
  FUN_18043e4c0(lVar1);
}
lVar1 = **(longlong **)(lVar1 + 0x90);
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x18185b014;
  FUN_18043e4c0(lVar1);
}
pOVar4 = (OWEndlessModule *)**(undefined8 **)(lVar1 + 0x28);
if (pOVar4 == (OWEndlessModule *)0x0) {
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185b0b4;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x18185b02e;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x1080b);
if (bVar2 == 0) {
  uStack_30 = 0x18185b03a;
  pEVar7 = OWEndlessModule::GetCurrentEndlessData(pOVar4);
  if (pEVar7 == (EndlessBaseData *)0x0) {
                  /* WARNING: Subroutine does not return */    uStack_30 = 0x18185b0a2;
    il2cpp::codegen::raise_null_reference_exception();
  }
  this_00 = (OWEndlessDataMode *)pEVar7->DataMode_k_BackingField;
}
else {
  uStack_30 = 0x18185b04f;
  pIVar6 = IFix::WrappersManagerImpl::GetPatch(0x1080b);
  if (pIVar6 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */    uStack_30 = 0x18185b0ae;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x18185b05f;
  this_00 = IFix::ILFixDynamicMethodWrapper::Gen_Wrap_7967                      ((ILFixDynamicMethodWrapper_57479 *)pIVar6,(undefined *)pOVar4);
}
if (this_00 == (OWEndlessDataMode *)0x0) {
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185b0a8;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x18185b06c;
OWEndlessDataMode::ResetDataMode(this_00);
uStack_30 = 0x18185aaa3;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x1edcb);
if (bVar2 != 0) {
  uStack_30 = 0x18185ac8e;
  pIVar6 = IFix::WrappersManagerImpl::GetPatch(0x1edcb);
  if (pIVar6 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */    uStack_30 = 0x18185acde;
    il2cpp::codegen::raise_null_reference_exception();
  }
  goto code_r0x000183b83b70;
}
uStack_30 = 0x18185aab8;
RefreshPlayerGroup(this);
uStack_30 = 0x18185aac0;
RefreshGroupList(this);
uStack_30 = 0x18185aac8;
RefreshInfo(this);
uStack_30 = 0x18185aad0;
RefreshInvade(this);
uStack_30 = 0x18185aad8;
RefreshReward(this);
uStack_30 = 0x18185aae0;
RefreshStyle(this);
lVar1 = *_DAT_189aa2678;
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x18185aafb;
  FUN_18043e4c0(lVar1);
}
lVar1 = **(longlong **)(lVar1 + 0x90);
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x18185ab16;
  FUN_18043e4c0(lVar1);
}
if ((WeeklyReportModule *)**(undefined8 **)(lVar1 + 0x28) == (WeeklyReportModule *)0x0) {
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185acd8;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x18185ab2b;
bVar2 = WeeklyReport::WeeklyReportModule::CanLobbyShowReport                  ((WeeklyReportModule *)**(undefined8 **)(lVar1 + 0x28));
uStack_30 = 0x18185ab36;
RefreshWeeklyReportTip(this,bVar2);
if (*(MonoOWEndlessAvatarLayout **)&this->Mode_k_BackingField == (MonoOWEndlessAvatarLayout *)0x0){
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185acd2;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x18185ab4b;
MonoOWEndlessAvatarLayout::Init(*(MonoOWEndlessAvatarLayout **)&this->Mode_k_BackingField,this);
if (*(MonoOWEndlessAvatarLayout **)&this->Mode_k_BackingField == (MonoOWEndlessAvatarLayout *)0x0){
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185accc;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x18185ab5d;
MonoOWEndlessAvatarLayout::RefreshView(*(MonoOWEndlessAvatarLayout **)&this->Mode_k_BackingField);
uStack_30 = 0x18185ab65;
pOVar4 = get_module(this);
if (pOVar4 == (OWEndlessModule *)0x0) {
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185acc6;
  il2cpp::codegen::raise_null_reference_exception();
}
if ((TwoEndless *)pOVar4->TwoEndless_k_BackingField == (TwoEndless *)0x0) {
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185acc0;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x18185ab80;
uVar3 = TwoEndless::GetActiveMode((TwoEndless *)pOVar4->TwoEndless_k_BackingField);
lVar1 = *_DAT_189a9c530;
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x18185ab9d;
  FUN_18043e4c0(lVar1);
}
lVar1 = **(longlong **)(lVar1 + 0x90);
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x18185abb8;
  FUN_18043e4c0(lVar1);
}
if ((OWEndlessModule *)**(undefined8 **)(lVar1 + 0x28) == (OWEndlessModule *)0x0) {
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185acba;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x18185abcd;
pCVar5 = OWEndlessModule::get_Config((OWEndlessModule *)**(undefined8 **)(lVar1 + 0x28));
if (pCVar5 == (ConfigOWEndless *)0x0) {
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185acb4;
  il2cpp::codegen::raise_null_reference_exception();
}
if (pCVar5->DebugData == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */  uStack_30 = 0x18185acae;
  il2cpp::codegen::raise_null_reference_exception();
}
if (pCVar5->DebugData[0x10] != '\0') {
  return;
}
if (uVar3 == 2) {
  if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
    uStack_30 = 0x18185ac28;
    il2cpp::codegen::runtime_class_init();
  }
  uVar3 = 2;
}
else {
  if (uVar3 != 3) goto LAB_18185ac32;
  if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
    uStack_30 = 0x18185ac0c;
    il2cpp::codegen::runtime_class_init();
  }
  uVar3 = 3;
}
uStack_30 = 0x18185ac32;
UIUtil::TryToShowEndlessReward(uVar3);
LAB_18185ac32:lVar1 = *_DAT_189a9c530;
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x18185ac4d;
  FUN_18043e4c0(lVar1);
}
lVar1 = **(longlong **)(lVar1 + 0x90);
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x18185ac68;
  FUN_18043e4c0(lVar1);
}
if ((OWEndlessModule *)**(undefined8 **)(lVar1 + 0x28) != (OWEndlessModule *)0x0) {
  uStack_30 = 0x18185ac79;
  OWEndlessModule::SafeShowOWEndlessTrapRewardDialog            ((OWEndlessModule *)**(undefined8 **)(lVar1 + 0x28));
  return;
}
                  /* WARNING: Subroutine does not return */uStack_30 = 0x18185aca8;
il2cpp::codegen::raise_null_reference_exception();
\