
uint gachaType;
longlong lVar1;
ApplicationManager *pAVar2;
byte bVar3;
Action *this_00;
undefined *puVar4;
Coroutine *pCVar5;
Transform *pTVar6;
GameObject *pGVar7;
KeyGeneratedEventHandler *this_01;
CGGMCLHFCNI *this_02;
CJPKGNKMFON *pCVar8;
ILFixDynamicMethodWrapper *pIVar9;
Call *pCVar10;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1814a2683;
bVar3 = IFix::WrappersManagerImpl::IsPatched(0x19a76);
if (bVar3 != 0) {
  uStack_30 = 0x1814a2937;
  pIVar9 = IFix::WrappersManagerImpl::GetPatch(0x19a76);
  if (pIVar9 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1814a298d;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar10 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar10->argumentBase;
  CStack_58.evaluationStackBase = pCVar10->evaluationStackBase;
  CStack_58.managedStack = pCVar10->managedStack;
  CStack_58.currentTop = pCVar10->currentTop;
  CStack_58.topWriteBack = pCVar10->topWriteBack;
  if (pIVar9->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar9->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar9->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar9->virtualMachine,pIVar9->methodId,&CStack_58,
               (pIVar9->anonObj != (undefined *)0x0) + 1,0);
    bVar3 = IFix::Core::Call::GetBoolean(&CStack_58,0);
    return bVar3;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
lVar1 = *_DAT_189a99490;
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x1814a26b5;
  FUN_18043e4c0(lVar1);
}
lVar1 = **(longlong **)(lVar1 + 0x90);
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x1814a26d0;
  FUN_18043e4c0(lVar1);
}
pAVar2 = (ApplicationManager *)**(undefined8 **)(lVar1 + 0x28);
if (*(int *)(_DAT_189a32350 + 0xe8) == 0) {
  uStack_30 = 0x1814a26ec;
  il2cpp::codegen::runtime_class_init();
}
this_00 = *(Action **)(*(longlong *)(_DAT_189a32350 + 0x28) + 8);
if (this_00 == (Action *)0x0) {
  if (*(int *)(_DAT_189a32350 + 0xe8) == 0) {
    uStack_30 = 0x1814a270d;
    il2cpp::codegen::runtime_class_init();
  }
  puVar4 = (undefined *)**(undefined8 **)(_DAT_189a32350 + 0x28);
  uStack_30 = 0x1814a2727;
  this_00 = (Action *)il2cpp::codegen::object_new(_DAT_1899defb0);
  uStack_30 = 0x1814a273c;
  KeyGeneratedEventHandler::_ctor((KeyGeneratedEventHandler *)this_00,puVar4,_DAT_189ad4780);
  *(Action **)(*(longlong *)(_DAT_189a32350 + 0x28) + 8) = this_00;
}
if (pAVar2 == (ApplicationManager *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1814a2987;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1814a275f;
ApplicationManager::InvokeNextFrame(pAVar2,this_00);
lVar1 = *_DAT_189a99490;
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x1814a277a;
  FUN_18043e4c0(lVar1);
}
lVar1 = **(longlong **)(lVar1 + 0x90);
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x1814a2795;
  FUN_18043e4c0(lVar1);
}
pAVar2 = (ApplicationManager *)**(undefined8 **)(lVar1 + 0x28);
uStack_30 = 0x1814a27a4;
puVar4 = ShowPlayerStatusBar(this);
if (pAVar2 == (ApplicationManager *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1814a2981;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1814a27bb;
pCVar5 = ApplicationManager::StartCoroutine(pAVar2,puVar4,1);
this->newItemDialogManager = (undefined *)pCVar5;
if ((GameObject *)this->view_k_BackingField == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1814a297b;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1814a27d4;
pTVar6 = UnityEngine::GameObject::get_transform((GameObject *)this->view_k_BackingField);
if (pTVar6 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1814a2975;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1814a27ec;
pTVar6 = UnityEngine::Transform::Find(pTVar6,_DAT_189b8bd90);
if (pTVar6 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1814a296f;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1814a27fd;
pGVar7 = UnityEngine::Component::get_gameObject((Component *)pTVar6);
if (pGVar7 == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1814a2969;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1814a2810;
UnityEngine::GameObject::SetActive(pGVar7,0);
uStack_30 = 0x1814a2818;
MergeAllMaterialAndSort(this);
uStack_30 = 0x1814a2824;
this_01 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_1899defb0);
uStack_30 = 0x1814a2839;
KeyGeneratedEventHandler::_ctor(this_01,(undefined *)this,_DAT_189ad4788);
uStack_30 = 0x1814a2845;
this_02 = (CGGMCLHFCNI *)il2cpp::codegen::object_new(_DAT_189a15ed8);
uStack_30 = 0x1814a2856;
CGGMCLHFCNI::_ctor(this_02,(Action *)this_01,(Action *)0x0);
this->OnDestroyEvent = (undefined *)this_02;
uStack_30 = 0x1814a2865;
InitNewStorageDialog(this);
uStack_30 = 0x1814a286d;
UpdateView(this);
uStack_30 = 0x1814a287f;
pGVar7 = BaseContext::SafeFindGameObject((BaseContext *)this,_DAT_189b6ea18,1);
lVar1 = *_DAT_189a9a530;
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x1814a289d;
  FUN_18043e4c0(lVar1);
}
lVar1 = **(longlong **)(lVar1 + 0x90);
if (*(char *)(lVar1 + 0x136) == '\0') {
  uStack_30 = 0x1814a28b8;
  FUN_18043e4c0(lVar1);
}
if ((LFKCAPPEIID *)**(undefined8 **)(lVar1 + 0x28) == (LFKCAPPEIID *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1814a2963;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1814a28cd;
bVar3 = LFKCAPPEIID::AKPPIDJDLDH((LFKCAPPEIID *)**(undefined8 **)(lVar1 + 0x28));
if (pGVar7 == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1814a295d;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1814a28e1;
UnityEngine::GameObject::SetActive(pGVar7,bVar3);
if ((HCHDIBFGCAL *)this->showPlayerStatusBarCoroutine != (HCHDIBFGCAL *)0x0) {
  uStack_30 = 0x1814a28f2;
  pCVar8 = HCHDIBFGCAL::PGKJBDNDLPN((HCHDIBFGCAL *)this->showPlayerStatusBarCoroutine);
  if (pCVar8 != (CJPKGNKMFON *)0x0) {
    gachaType = pCVar8->NIBNPDHPGKH;
    if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
      uStack_30 = 0x1814a290f;
      il2cpp::codegen::runtime_class_init();
    }
    uStack_30 = 0x1814a2916;
    UIUtil::SetPlayerStatusByGachaInfo(gachaType);
    return 0;
  }
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1814a2951;
  il2cpp::codegen::raise_null_reference_exception();
}
                  /* WARNING: Subroutine does not return */
uStack_30 = 0x1814a2957;
il2cpp::codegen::raise_null_reference_exception();\