
undefined2 uVar1;
MainUIManager *this;
BaseDialogContext *dialogContext;
DateTime *d2;
Component *this_00;
code *pcVar2;
longlong *plVar3;
double dVar4;
bool bVar5;
byte bVar6;
char cVar7;
ILFixDynamicMethodWrapper *pIVar8;
longlong lVar9;
CanvasTimer *pCVar10;
Transform *pTVar11;
BasePageContext *currentPage;
BaseContext *pBVar12;
Transform *pTVar13;
DateTime *d1;
MiHoYoGameData *this_01;
DKCCFNENGLA *this_02;
MainPageContext *this_03;
Call *pCVar14;
GameObject *this_04;
KeyGeneratedEventHandler *pKVar15;
CGGMCLHFCNI *this_05;
undefined *puVar16;
DropNewItemDialogContextV2 *this_06;
undefined8 uVar17;
ulonglong uVar18;
undefined1 *puVar19;
ulonglong uVar20;
float fVar21;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x18529479e;
bVar6 = IFix::WrappersManagerImpl::IsPatched(0x18426);
if (bVar6 != 0) {
  uStack_30 = 0x1852948f9;
  pIVar8 = IFix::WrappersManagerImpl::GetPatch(0x18426);
  if (pIVar8 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18529492d;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar14 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar14->argumentBase;
  CStack_58.evaluationStackBase = pCVar14->evaluationStackBase;
  CStack_58.managedStack = pCVar14->managedStack;
  CStack_58.currentTop = pCVar14->currentTop;
  CStack_58.topWriteBack = pCVar14->topWriteBack;
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
lVar9 = *_DAT_189a985c0;
if (*(char *)(lVar9 + 0x136) == '\0') {
  uStack_30 = 0x1852947c6;
  FUN_18043e4c0(lVar9);
}
lVar9 = **(longlong **)(lVar9 + 0x90);
if (*(char *)(lVar9 + 0x136) == '\0') {
  uStack_30 = 0x1852947e1;
  FUN_18043e4c0(lVar9);
}
if (**(longlong **)(lVar9 + 0x28) == 0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x185294927;
  il2cpp::codegen::raise_null_reference_exception();
}
this_00 = *(Component **)(**(longlong **)(lVar9 + 0x28) + 0x10);
if (this_00 == (Component *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x185294921;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x185294803;
this_04 = UnityEngine::Component::get_gameObject(this_00);
if (this_04 == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x18529491b;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x18529481b;
UnityEngine::GameObject::SetActive(this_04,1);
uStack_30 = 0x185294827;
pKVar15 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_1899defb0);
uStack_30 = 0x18529483b;
KeyGeneratedEventHandler::_ctor(pKVar15,(undefined *)0x0,_DAT_189ac56a0);
uStack_30 = 0x185294847;
this_05 = (CGGMCLHFCNI *)il2cpp::codegen::object_new(_DAT_189a15ed8);
uStack_30 = 0x185294858;
CGGMCLHFCNI::_ctor(this_05,(Action *)pKVar15,(Action *)0x0);
lVar9 = *_DAT_189a9b3d8;
if (*(char *)(lVar9 + 0x136) == '\0') {
  uStack_30 = 0x185294873;
  FUN_18043e4c0(lVar9);
}
lVar9 = **(longlong **)(lVar9 + 0x90);
if (*(char *)(lVar9 + 0x136) == '\0') {
  uStack_30 = 0x18529488e;
  FUN_18043e4c0(lVar9);
}
if ((HCHDIBFGCAL *)**(undefined8 **)(lVar9 + 0x28) == (HCHDIBFGCAL *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x185294915;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1852948a4;
puVar16 = HCHDIBFGCAL::JECIFOHCFHP((HCHDIBFGCAL *)**(undefined8 **)(lVar9 + 0x28));
uStack_30 = 0x1852948b3;
this_06 = (DropNewItemDialogContextV2 *)il2cpp::codegen::object_new(_DAT_189a2b458);
uStack_30 = 0x1852948c1;
DropNewItemDialogContextV2::_ctor(this_06,puVar16);
if (this_05 == (CGGMCLHFCNI *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x18529490f;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1852948d1;
CGGMCLHFCNI::DGOHOCLIJID(this_05,(BaseSequenceDialogContext *)this_06);
CStack_58.currentTop = (undefined *)0x180712fdb;
bVar6 = IFix::WrappersManagerImpl::IsPatched(0xccc8);
if (bVar6 != 0) {
  CStack_58.currentTop = (undefined *)0x180713154;
  pIVar8 = IFix::WrappersManagerImpl::GetPatch(0xccc8);
  if (pIVar8 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.currentTop = (undefined *)0x1807131a0;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  pCVar14 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar14->managedStack;
  CStack_58.evaluationStackBase = pCVar14->currentTop;
  CStack_58.managedStack = pCVar14->topWriteBack;
  if (pIVar8->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject((Call *)&stack0xffffffffffffff98,pIVar8->anonObj);
  }
  IFix::Core::Call::PushObject((Call *)&stack0xffffffffffffff98,(undefined *)this_05);
  IFix::Core::Call::PushSingle((Call *)&stack0xffffffffffffff98,0.0);
  if ((VirtualMachine *)pIVar8->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar8->virtualMachine,pIVar8->methodId,
             (Call *)&stack0xffffffffffffff98,(pIVar8->anonObj != (undefined *)0x0) + 2,0);
  return;
}
CStack_58.currentTop = (undefined *)0x180712fee;
bVar6 = UnityEngine::Mathf::Approximately(0.0,0.0);
if (bVar6 == 0) {
  lVar9 = *_DAT_189a985c0;
  if (*(char *)(lVar9 + 0x136) == '\0') {
    CStack_58.currentTop = (undefined *)0x180713016;
    FUN_18043e4c0(lVar9);
  }
  lVar9 = **(longlong **)(lVar9 + 0x90);
  if (*(char *)(lVar9 + 0x136) == '\0') {
    CStack_58.currentTop = (undefined *)0x180713031;
    FUN_18043e4c0(lVar9);
  }
  if (**(longlong **)(lVar9 + 0x28) == 0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.currentTop = (undefined *)0x180713194;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.currentTop = (undefined *)0x18071304c;
  bVar6 = UnityEngine::Object::op_Inequality
                    (*(Object **)(**(longlong **)(lVar9 + 0x28) + 0x10),(Object *)0x0);
  if (bVar6 != 0) {
    if (this_05->IGHJDGOBBJB != (undefined *)0x0) {
      CStack_58.currentTop = (undefined *)0x180713067;
      lVar9 = FUN_180261460(_DAT_189a985c0);
      if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x18071317c;
        il2cpp::codegen::raise_null_reference_exception();
      }
      if (*(BaseMonoCanvas **)(lVar9 + 0x10) == (BaseMonoCanvas *)0x0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x180713176;
        il2cpp::codegen::raise_null_reference_exception();
      }
      CStack_58.currentTop = (undefined *)0x180713086;
      BaseMonoCanvas::RemoveTimer
                (*(BaseMonoCanvas **)(lVar9 + 0x10),(CanvasTimer *)this_05->IGHJDGOBBJB);
    }
    CStack_58.currentTop = (undefined *)0x180713092;
    lVar9 = FUN_180261460(_DAT_189a985c0);
    if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x18071318e;
      il2cpp::codegen::raise_null_reference_exception();
    }
    if (*(BaseMonoCanvas **)(lVar9 + 0x10) == (BaseMonoCanvas *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x180713188;
      il2cpp::codegen::raise_null_reference_exception();
    }
    CStack_58.currentTop = (undefined *)0x1807130b8;
    pCVar10 = BaseMonoCanvas::CreateTimer(*(BaseMonoCanvas **)(lVar9 + 0x10),0.0,0.0);
    this_05->IGHJDGOBBJB = (undefined *)pCVar10;
    CStack_58.currentTop = (undefined *)0x1807130cb;
    pKVar15 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_1899defb0);
    CStack_58.currentTop = (undefined *)0x1807130e0;
    KeyGeneratedEventHandler::_ctor(pKVar15,(undefined *)this_05,_DAT_189b05570);
    if (pCVar10 == (CanvasTimer *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x180713182;
      il2cpp::codegen::raise_null_reference_exception();
    }
    pCVar10->timeUpCallback = (undefined *)pKVar15;
  }
  return;
}
CStack_58.currentTop = (undefined *)0x18071310c;
bVar6 = IFix::WrappersManagerImpl::IsPatched(0xccc9);
if (bVar6 != 0) {
  CStack_58.currentTop = (undefined *)0x180713130;
  pIVar8 = IFix::WrappersManagerImpl::GetPatch(0xccc9);
  if (pIVar8 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.currentTop = (undefined *)0x18071319a;
    il2cpp::codegen::raise_null_reference_exception();
  }
IFix_ILFixDynamicMethodWrapper_Gen_Wrap_13:
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar14 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar14->argumentBase;
  CStack_58.evaluationStackBase = pCVar14->evaluationStackBase;
  CStack_58.managedStack = pCVar14->managedStack;
  CStack_58.currentTop = pCVar14->currentTop;
  CStack_58.topWriteBack = pCVar14->topWriteBack;
  if (pIVar8->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar8->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this_05);
  if ((VirtualMachine *)pIVar8->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar8->virtualMachine,pIVar8->methodId,&CStack_58,
             (pIVar8->anonObj != (undefined *)0x0) + 1,0);
  return;
}
this_05->HMBPLPCHLIP = 1;
uStack_30 = 0x180712a93;
bVar6 = IFix::WrappersManagerImpl::IsPatched(0xccc6);
if (bVar6 != 0) {
  uStack_30 = 0x180712b4b;
  pIVar8 = IFix::WrappersManagerImpl::GetPatch(0xccc6);
  if (pIVar8 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x180712b77;
    il2cpp::codegen::raise_null_reference_exception();
  }
  goto IFix_ILFixDynamicMethodWrapper_Gen_Wrap_13;
}
if (this_05->OAOPMKOFNLP == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x180712b71;
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(int *)(this_05->OAOPMKOFNLP + 0x18) < 1) {
  uStack_30 = 0x180712df3;
  bVar6 = IFix::WrappersManagerImpl::IsPatched(0xccc5);
  if (bVar6 == 0) {
    puVar16 = this_05->MPNINDEJPHF;
    this_05->HMBPLPCHLIP = 0;
    if (puVar16 == (undefined *)0x0) {
      return;
    }
    lVar9 = *(longlong *)(puVar16 + 0x68);
    if (lVar9 == 0) {
      uVar20 = 1;
      puVar19 = &stack0x00000008;
    }
    else {
      uVar20 = *(ulonglong *)(lVar9 + 0x18);
      puVar19 = (undefined1 *)(lVar9 + 0x20);
    }
    uVar18 = 0;
    if (uVar20 != 0) {
      do {
        lVar9 = *(longlong *)(puVar19 + uVar18 * 8);
        pcVar2 = *(code **)(lVar9 + 0x10);
        plVar3 = *(longlong **)(lVar9 + 0x20);
        lVar9 = *(longlong *)(lVar9 + 0x28);
        if (*(short *)(lVar9 + 0x30) == -1) {
          CStack_58.evaluationStackBase = (undefined *)0x186ae440f;
          thunk_FUN_180448910(lVar9);
        }
        CStack_58.evaluationStackBase = (undefined *)0x186ae4417;
        cVar7 = FUN_1804fe050(lVar9);
        if (cVar7 == '\0') {
          if ((((plVar3 == (longlong *)0x0) || (*(short *)(lVar9 + 0x30) == -1)) ||
              ((*(uint *)(*plVar3 + 0x10c) >> 8 & 1) != 0)) ||
             (*(longlong *)(puVar16 + 0x18) == 0)) goto LAB_186ae44cb;
          CStack_58.evaluationStackBase = (undefined *)0x186ae4463;
          cVar7 = thunk_FUN_180442270(lVar9);
          if (cVar7 == '\0') {
            CStack_58.evaluationStackBase = (undefined *)0x186ae448c;
            cVar7 = FUN_1804fe3a0(lVar9);
            if (cVar7 == '\0') {
              CStack_58.evaluationStackBase = (undefined *)0x186ae44c9;
              (**(code **)(*plVar3 + 0x148 + (ulonglong)*(ushort *)(lVar9 + 0x30) * 0x10))
                        (plVar3,*(undefined8 *)
                                 (*plVar3 + 0x150 + (ulonglong)*(ushort *)(lVar9 + 0x30) * 0x10));
            }
            else {
              uVar1 = *(undefined2 *)(lVar9 + 0x30);
              CStack_58.evaluationStackBase = (undefined *)0x186ae449c;
              uVar17 = thunk_FUN_180432d70(lVar9);
              CStack_58.evaluationStackBase = (undefined *)0x186ae44a9;
              FUN_180257630(uVar1,uVar17,plVar3);
            }
          }
          else {
            CStack_58.evaluationStackBase = (undefined *)0x186ae446f;
            cVar7 = FUN_1804fe3a0(lVar9);
            if (cVar7 == '\0') {
              CStack_58.evaluationStackBase = (undefined *)0x186ae4485;
              FUN_180306e50(lVar9,plVar3);
            }
            else {
              CStack_58.evaluationStackBase = (undefined *)0x186ae447e;
              FUN_1802ced20();
            }
          }
        }
        else if (*(char *)(lVar9 + 0x32) == '\0') {
          CStack_58.evaluationStackBase = (undefined *)0x186ae442a;
          (*pcVar2)(lVar9);
        }
        else {
LAB_186ae44cb:
          CStack_58.evaluationStackBase = (undefined *)0x186ae44d3;
          (*pcVar2)(plVar3,lVar9);
        }
        uVar18 = uVar18 + 1;
      } while (uVar18 < uVar20);
    }
    return;
  }
  uStack_30 = 0x180712e1d;
  pIVar8 = IFix::WrappersManagerImpl::GetPatch(0xccc5);
  if (pIVar8 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x180712e37;
    il2cpp::codegen::raise_null_reference_exception();
  }
  goto IFix_ILFixDynamicMethodWrapper_Gen_Wrap_13;
}
if ((Action *)this_05->PHOFPDEFGHN != (Action *)0x0) {
  uStack_30 = 0x180712ace;
  System::Action::Invoke((Action *)this_05->PHOFPDEFGHN);
}
lVar9 = *_DAT_189a985c0;
if (*(char *)(lVar9 + 0x136) == '\0') {
  uStack_30 = 0x180712ae9;
  FUN_18043e4c0(lVar9);
}
lVar9 = **(longlong **)(lVar9 + 0x90);
if (*(char *)(lVar9 + 0x136) == '\0') {
  uStack_30 = 0x180712b04;
  FUN_18043e4c0(lVar9);
}
puVar16 = this_05->OAOPMKOFNLP;
this = (MainUIManager *)**(undefined8 **)(lVar9 + 0x28);
if (puVar16 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x180712b6b;
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(int *)(puVar16 + 0x18) == 0) {
  uStack_30 = 0x180712b1f;
  System::ThrowHelper::ThrowArgumentOutOfRangeException();
}
if (this == (MainUIManager *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x180712b65;
  il2cpp::codegen::raise_null_reference_exception();
}
dialogContext = *(BaseDialogContext **)(*(longlong *)(puVar16 + 0x10) + 0x20);
CStack_58.evaluationStackBase = (undefined *)0x180926c53;
bVar6 = IFix::WrappersManagerImpl::IsPatched(0x70f);
if (bVar6 != 0) {
  CStack_58.evaluationStackBase = (undefined *)0x180926f26;
  pIVar8 = IFix::WrappersManagerImpl::GetPatch(0x70f);
  if (pIVar8 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.evaluationStackBase = (undefined *)0x180926f8c;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.evaluationStackBase = (undefined *)0x180926f3c;
  IFix::ILFixDynamicMethodWrapper::Gen_Wrap_16
            ((ILFixDynamicMethodWrapper_57479 *)pIVar8,(undefined *)this,
             (undefined *)dialogContext,0);
  return;
}
if (dialogContext == (BaseDialogContext *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f86;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x180926c6c;
bVar6 = BaseContext::CheckResReady((BaseContext *)dialogContext);
if (bVar6 == 0) {
  return;
}
CStack_58.evaluationStackBase = (undefined *)0x180926c7f;
bVar6 = UnityEngine::Object::CompareBaseObjects
                  ((Object *)this->SceneCanvas_k_BackingField,(Object *)0x0);
if (bVar6 != 0) {
  return;
}
CStack_58.evaluationStackBase = (undefined *)0x180926c9e;
pTVar11 = MainUIManager::GetUIHolder(this,dialogContext->uiType);
if (this->pageContextStack == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f80;
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(int *)(this->pageContextStack + 0x18) < 1) {
  CStack_58.evaluationStackBase = (undefined *)0x180926cc4;
  lVar9 = func_0x000180257760(this->SceneCanvas_k_BackingField,_DAT_189a157f0);
  if (lVar9 != 0) {
    CStack_58.evaluationStackBase = (undefined *)0x180926cd1;
    bVar6 = MainUIManager::HasContextInStash(this);
    if (bVar6 != 0) {
      CStack_58.evaluationStackBase = (undefined *)0x180926cdd;
      MainUIManager::RecoveryPageStackFromStashOnly(this);
    }
  }
}
puVar16 = this->pageContextStack;
if (puVar16 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f7a;
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(int *)(puVar16 + 0x18) < 1) {
  CStack_58.evaluationStackBase = (undefined *)0x180926d05;
  lVar9 = func_0x000180257760(this->SceneCanvas_k_BackingField,_DAT_189a157f0);
  if (lVar9 == 0) {
    currentPage = (BasePageContext *)this->emptyPageContext;
    if (currentPage != (BasePageContext *)0x0) goto LAB_180926d4f;
  }
  else {
    CStack_58.evaluationStackBase = (undefined *)0x180926ef5;
    this_03 = (MainPageContext *)il2cpp::codegen::object_new(_DAT_189a16920);
    CStack_58.evaluationStackBase = (undefined *)0x180926f00;
    MainPageContext::_ctor(this_03);
    if (puVar16 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.evaluationStackBase = (undefined *)0x180926f4a;
      il2cpp::codegen::raise_null_reference_exception();
    }
    CStack_58.evaluationStackBase = (undefined *)0x180926f17;
    FUN_185585c90(puVar16,this_03);
  }
}
puVar16 = this->pageContextStack;
if (puVar16 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f74;
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(int *)(puVar16 + 0x18) < 1) {
  return;
}
if (puVar16 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f6e;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x180926d43;
currentPage = (BasePageContext *)FUN_185585a70(puVar16,_DAT_189ab5e90);
if (currentPage == (BasePageContext *)0x0) {
  return;
}
LAB_180926d4f:
CStack_58.evaluationStackBase = (undefined *)0x180926d5a;
pBVar12 = MainUIManager::GetTheLastContext(this,currentPage);
CStack_58.evaluationStackBase = (undefined *)0x180926d6b;
MainUIManager::HandleTopContextParticleNodesActive(this,currentPage,0);
if (currentPage == (BasePageContext *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f68;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x180926d7f;
BasePageContext::AddDialog(currentPage,dialogContext);
if (pBVar12 != (BaseContext *)0x0) {
  CStack_58.evaluationStackBase = (undefined *)0x180926d98;
  (**(code **)(pBVar12->__klass + 0x308))(pBVar12,*(undefined8 *)(pBVar12->__klass + 0x310));
}
dialogContext->pageContext = (undefined *)currentPage;
if ((Component *)this->SceneCanvas_k_BackingField == (Component *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x180926f62;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x180926db1;
pTVar13 = UnityEngine::Component::get_transform((Component *)this->SceneCanvas_k_BackingField);
CStack_58.evaluationStackBase = (undefined *)0x180926dcb;
(**(code **)(dialogContext->__klass + 0x188))
          (dialogContext,pTVar13,pTVar11,*(undefined8 *)(dialogContext->__klass + 400));
CStack_58.evaluationStackBase = (undefined *)0x180926dd9;
MainUIManager::HandleTopContextParticleNodesActive(this,currentPage,1);
bVar5 = false;
if ((char)(this->lastTimeToReportPlayerSpendTimeData).TicksPerSecond != '\0') {
  if (*(int *)(_DAT_189a15420 + 0xe8) == 0) {
    CStack_58.evaluationStackBase = (undefined *)0x180926dff;
    il2cpp::codegen::runtime_class_init();
  }
  CStack_58.evaluationStackBase = (undefined *)0x180926e04;
  d1 = TimeUtil::get_NowDateTime();
  d2 = (DateTime *)(this->lastTimeToReportPlayerSpendTimeData).TicksPerMillisecond;
  if (*(int *)(_DAT_1899de528 + 0xe8) == 0) {
    CStack_58.evaluationStackBase = (undefined *)0x180926e20;
    il2cpp::codegen::runtime_class_init();
  }
  CStack_58.evaluationStackBase = (undefined *)0x180926e2b;
  System::DateTime::op_Subtraction(d1,d2);
  CStack_58.evaluationStackBase = (undefined *)0x180926e3a;
  dVar4 = System::TimeSpan::get_TotalSeconds((TimeSpan *)&stack0x00000020);
  if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
    CStack_58.evaluationStackBase = (undefined *)0x180926e52;
    il2cpp::codegen::runtime_class_init();
  }
  CStack_58.evaluationStackBase = (undefined *)0x180926e57;
  fVar21 = ExcelMeta::ConstValueDataReaderExtend::get_CDTimeToReportPlayerSpeedTimeData();
  bVar5 = (double)fVar21 < dVar4;
  if ((double)fVar21 < dVar4) {
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
MainUIManager::RecordShowContext(this,(BaseContext *)dialogContext);
if (bVar5) {
  CStack_58.evaluationStackBase = (undefined *)0x180926eb7;
  MainUIManager::TryToSendPlayerSpendTimeDataToServer(this,0);
}
if ((AsyncCallback *)this->OnDialogShow != (AsyncCallback *)0x0) {
  if (dialogContext->config == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.evaluationStackBase = (undefined *)0x180926f5c;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.evaluationStackBase = (undefined *)0x180926ed6;
  System::AsyncCallback::Invoke
            ((AsyncCallback *)this->OnDialogShow,*(undefined **)(dialogContext->config + 0x10));
}
return;\