
undefined *puVar1;
bool bVar2;
byte bVar3;
char cVar4;
int iVar5;
Transform *pTVar6;
longlong *plVar7;
undefined8 *puVar8;
longlong *plVar9;
longlong *plVar10;
MonoLevelDropIconButton *this_00;
longlong lVar11;
ILFixDynamicMethodWrapper *this_01;
ushort uVar12;

bVar3 = IFix::WrappersManagerImpl::IsPatched(0x19a9d);
if (bVar3 == 0) {
  if ((ArrayList *)this->DROP_ITEM_ANIMATION_NAME == (ArrayList *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  System::Collections::ArrayList::Clear((ArrayList *)this->DROP_ITEM_ANIMATION_NAME);
  *(undefined4 *)&this->dropList = 0;
  if ((GameObject *)this->view_k_BackingField == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pTVar6 = UnityEngine::GameObject::get_transform((GameObject *)this->view_k_BackingField);
  if (pTVar6 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pTVar6 = UnityEngine::Transform::Find(pTVar6,_DAT_189baf078);
  if (pTVar6 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  plVar7 = (longlong *)UnityEngine::Transform::GetEnumerator(pTVar6);
  while( true ) {
    if (plVar7 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    cVar4 = FUN_180257840(0,_DAT_1899de560,plVar7);
    if (cVar4 == '\0') break;
    lVar11 = *plVar7;
    uVar12 = 0;
    if (*(ushort *)(lVar11 + 0x12e) != 0) {
      do {
        if (*(longlong *)(*(longlong *)(lVar11 + 0x70) + (ulonglong)uVar12 * 0x10) ==
            _DAT_1899de560) {
          puVar8 = (undefined8 *)
                   (lVar11 + 0x148 +
                   (ulonglong)
                   (*(int *)(*(longlong *)(lVar11 + 0x70) + 8 + (ulonglong)uVar12 * 0x10) + 1) *
                   0x10);
          goto LAB_1814a03b6;
        }
        uVar12 = uVar12 + 1;
      } while (uVar12 < *(ushort *)(lVar11 + 0x12e));
    }
    puVar8 = (undefined8 *)FUN_1804363c0(plVar7,_DAT_1899de560,1);
LAB_1814a03b6:
    plVar9 = (longlong *)(*(code *)*puVar8)(plVar7,puVar8[1]);
    if (plVar9 == (longlong *)0x0) goto LAB_1814a053a;
    lVar11 = *plVar9;
    if ((*(byte *)(lVar11 + 0x132) < *(byte *)(_DAT_1899e5460 + 0x132)) ||
       (bVar2 = true,
       *(longlong *)
        (*(longlong *)(lVar11 + 0x50) + (longlong)(int)(*(byte *)(_DAT_1899e5460 + 0x132) - 1) * 8
        ) != _DAT_1899e5460)) {
      bVar2 = false;
    }
    plVar10 = (longlong *)0x0;
    if (bVar2) {
      plVar10 = plVar9;
    }
    if (plVar10 == (longlong *)0x0) {
LAB_1814a0532:
      FUN_1804fe070(plVar9);
LAB_1814a053a:
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    if ((*(byte *)(lVar11 + 0x132) < *(byte *)(_DAT_1899e5460 + 0x132)) ||
       (bVar2 = true,
       *(longlong *)
        (*(longlong *)(lVar11 + 0x50) + (longlong)(int)(*(byte *)(_DAT_1899e5460 + 0x132) - 1) * 8
        ) != _DAT_1899e5460)) {
      bVar2 = false;
    }
    plVar10 = (longlong *)0x0;
    if (bVar2) {
      plVar10 = plVar9;
    }
    if (plVar10 == (longlong *)0x0) {
      FUN_1804fe070(plVar9);
      goto LAB_1814a0532;
    }
    this_00 = (MonoLevelDropIconButton *)FUN_183978ec0();
    bVar3 = UnityEngine::Object::CompareBaseObjects((Object *)this_00,(Object *)0x0);
    if (bVar3 == 0) {
      if (this_00 == (MonoLevelDropIconButton *)0x0) {
                  /* WARNING: Subroutine does not return */
        il2cpp::codegen::raise_null_reference_exception();
      }
      MonoLevelDropIconButton::StopRareEffect(this_00);
      puVar1 = this->rareItemList;
      iVar5 = MonoLevelDropIconButton::GetDropItemID(this_00);
      if (puVar1 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        il2cpp::codegen::raise_null_reference_exception();
      }
      cVar4 = FUN_1851b0e50(puVar1,iVar5,0);
      if (((cVar4 == '\0') && (bVar3 = MonoLevelDropIconButton::IsAvatarCard(this_00), bVar3 == 0)
          ) && (bVar3 = MonoLevelDropIconButton::IsAvatarFragment(this_00), bVar3 == 0)) {
        bVar3 = MonoLevelDropIconButton::IsSpliteMaterial(this_00);
        if (bVar3 != 0) {
          if (this->DROP_ITEM_ANIMATION_NAME == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
            il2cpp::codegen::raise_null_reference_exception();
          }
          FUN_184c69c50(this->DROP_ITEM_ANIMATION_NAME,this_00,_DAT_189aa0990);
        }
      }
      else {
        if (this->DROP_ITEM_ANIMATION_NAME == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
          il2cpp::codegen::raise_null_reference_exception();
        }
        FUN_184c69c50(this->DROP_ITEM_ANIMATION_NAME,this_00,_DAT_189aa0990);
        *(int *)&this->dropList = *(int *)&this->dropList + 1;
      }
    }
  }
  lVar11 = thunk_FUN_180442320(plVar7,_DAT_1899de570);
  if (lVar11 != 0) {
    FUN_180257630(0,_DAT_1899de570,lVar11);
  }
}
else {
  this_01 = IFix::WrappersManagerImpl::GetPatch(0x19a9d);
  if (this_01 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::ILFixDynamicMethodWrapper::Gen_Wrap_13(this_01,(undefined *)this);
}
return;\