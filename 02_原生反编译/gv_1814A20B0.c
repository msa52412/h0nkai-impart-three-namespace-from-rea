
MonoLevelDropIconButton *this_00;
float fVar1;
byte bVar2;
int iVar3;
GameObject *x;
Transform *pTVar4;
ILFixDynamicMethodWrapper *pIVar5;
Call *pCVar6;
undefined *puVar7;
uint uVar8;
longlong lVar9;
float delay;
Call aCStack_58 [2];

aCStack_58[0].evaluationStackBase = (undefined *)0x1814a20c3;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x19a9c);
fVar1 = _DAT_18797803c;
if (bVar2 != 0) {
  aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2239;
  pIVar5 = IFix::WrappersManagerImpl::GetPatch(0x19a9c);
  if (pIVar5 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2283;
    il2cpp::codegen::raise_null_reference_exception();
  }
  aCStack_58[0].argumentBase = (undefined *)0x0;
  aCStack_58[0].evaluationStackBase = (undefined *)0x0;
  aCStack_58[0].managedStack = (undefined *)0x0;
  aCStack_58[0].currentTop = (undefined *)0x0;
  aCStack_58[0].topWriteBack = (undefined *)0x0;
  pCVar6 = IFix::Core::Call::Begin();
  aCStack_58[0].argumentBase = pCVar6->argumentBase;
  aCStack_58[0].evaluationStackBase = pCVar6->evaluationStackBase;
  aCStack_58[0].managedStack = pCVar6->managedStack;
  aCStack_58[0].currentTop = pCVar6->currentTop;
  aCStack_58[0].topWriteBack = pCVar6->topWriteBack;
  if (pIVar5->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(aCStack_58,pIVar5->anonObj);
  }
  IFix::Core::Call::PushObject(aCStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar5->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar5->virtualMachine,pIVar5->methodId,aCStack_58,
             (pIVar5->anonObj != (undefined *)0x0) + 1,0);
  return;
}
puVar7 = this->DROP_ITEM_ANIMATION_NAME;
uVar8 = 0;
if (puVar7 != (undefined *)0x0) {
  lVar9 = 0x20;
  delay = _DAT_187979820;
  do {
    if (*(int *)(puVar7 + 0x18) <= (int)uVar8) {
      if ((GameObject *)this->view_k_BackingField == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
        aCStack_58[0].evaluationStackBase = (undefined *)0x1814a227d;
        il2cpp::codegen::raise_null_reference_exception();
      }
      aCStack_58[0].evaluationStackBase = (undefined *)0x1814a21cf;
      pTVar4 = UnityEngine::GameObject::get_transform((GameObject *)this->view_k_BackingField);
      if (pTVar4 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
        aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2277;
        il2cpp::codegen::raise_null_reference_exception();
      }
      aCStack_58[0].evaluationStackBase = (undefined *)0x1814a21e7;
      pTVar4 = UnityEngine::Transform::Find(pTVar4,_DAT_189baf070);
      if (pTVar4 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
        aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2271;
        il2cpp::codegen::raise_null_reference_exception();
      }
      aCStack_58[0].evaluationStackBase = (undefined *)0x1814a21ff;
      lVar9 = FUN_183978ec0(pTVar4,_DAT_189ad47a8);
      if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
        aCStack_58[0].evaluationStackBase = (undefined *)0x1814a226b;
        il2cpp::codegen::raise_null_reference_exception();
      }
      *(undefined1 *)(lVar9 + 0x59) = 1;
      return;
    }
    if (puVar7 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
      aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2265;
      il2cpp::codegen::raise_null_reference_exception();
    }
    if (*(uint *)(puVar7 + 0x18) <= uVar8) {
      aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2130;
      System::ThrowHelper::ThrowArgumentOutOfRangeException();
    }
    this_00 = *(MonoLevelDropIconButton **)(lVar9 + *(longlong *)(puVar7 + 0x10));
    aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2142;
    bVar2 = UnityEngine::Object::op_Inequality((Object *)this_00,(Object *)0x0);
    if (bVar2 != 0) {
      if (this_00 == (MonoLevelDropIconButton *)0x0) {
                  /* WARNING: Subroutine does not return */
        aCStack_58[0].evaluationStackBase = (undefined *)0x1814a225f;
        il2cpp::codegen::raise_null_reference_exception();
      }
      aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2157;
      x = UnityEngine::Component::get_gameObject((Component *)this_00);
      aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2161;
      bVar2 = UnityEngine::Object::op_Inequality((Object *)x,(Object *)0x0);
      if (bVar2 != 0) {
        puVar7 = this->rareItemList;
        aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2174;
        iVar3 = MonoLevelDropIconButton::GetDropItemID(this_00);
        if (puVar7 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
          aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2259;
          il2cpp::codegen::raise_null_reference_exception();
        }
        aCStack_58[0].evaluationStackBase = (undefined *)0x1814a218a;
        bVar2 = FUN_1851b0e50(puVar7,iVar3,0);
        aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2199;
        MonoLevelDropIconButton::PlayVFX(this_00,delay,bVar2);
        delay = delay + fVar1;
      }
    }
    puVar7 = this->DROP_ITEM_ANIMATION_NAME;
    uVar8 = uVar8 + 1;
    lVar9 = lVar9 + 8;
  } while (puVar7 != (undefined *)0x0);
}
                  /* WARNING: Subroutine does not return */
aCStack_58[0].evaluationStackBase = (undefined *)0x1814a2253;
il2cpp::codegen::raise_null_reference_exception();\