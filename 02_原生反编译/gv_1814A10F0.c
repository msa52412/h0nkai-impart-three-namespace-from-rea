
ApplicationManager *pAVar1;
bool bVar2;
float value;
byte bVar3;
char cVar4;
undefined *puVar5;
Transform *pTVar6;
longlong *plVar7;
undefined8 *puVar8;
longlong *plVar9;
CanvasGroup *this_00;
longlong lVar10;
ILFixDynamicMethodWrapper *this_01;
ushort uVar11;
longlong *plVar12;
float delay;
undefined4 auStack_98 [6];
undefined8 uStack_80;
undefined4 *puStack_68;
undefined4 uStack_60;

uStack_80 = 0xfffffffffffffffe;
puStack_68 = auStack_98;
uStack_60 = 0xffffffff;
bVar3 = IFix::WrappersManagerImpl::IsPatched(0x19a8c);
if (bVar3 == 0) {
  if (this->newItemDialogManager != (undefined *)0x0) {
    lVar10 = *_DAT_189a99490;
    if (*(char *)(lVar10 + 0x136) == '\0') {
      FUN_18043e4c0(lVar10);
    }
    lVar10 = **(longlong **)(lVar10 + 0x90);
    if (*(char *)(lVar10 + 0x136) == '\0') {
      FUN_18043e4c0(lVar10);
    }
    if ((ApplicationManager *)**(undefined8 **)(lVar10 + 0x28) == (ApplicationManager *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    ApplicationManager::StopCoroutine
              ((ApplicationManager *)**(undefined8 **)(lVar10 + 0x28),
               (Coroutine *)this->newItemDialogManager);
  }
  lVar10 = *_DAT_189a99490;
  if (*(char *)(lVar10 + 0x136) == '\0') {
    FUN_18043e4c0(lVar10);
  }
  lVar10 = **(longlong **)(lVar10 + 0x90);
  if (*(char *)(lVar10 + 0x136) == '\0') {
    FUN_18043e4c0(lVar10);
  }
  pAVar1 = (ApplicationManager *)**(undefined8 **)(lVar10 + 0x28);
  puVar5 = ShowPlayerStatusBarOnAnimationEnd(this);
  if (pAVar1 == (ApplicationManager *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  ApplicationManager::StartCoroutine(pAVar1,puVar5,1);
  value = _DAT_187975b88;
  delay = _DAT_187975b74;
  if (0 < *(int *)&this->dropList) {
    delay = (float)(*(int *)&this->dropList + -1) * _DAT_18797803c + _DAT_187975b88 +
            _DAT_187975b74;
  }
  lVar10 = *_DAT_189a99490;
  if (*(char *)(lVar10 + 0x136) == '\0') {
    FUN_18043e4c0(lVar10);
  }
  lVar10 = **(longlong **)(lVar10 + 0x90);
  if (*(char *)(lVar10 + 0x136) == '\0') {
    FUN_18043e4c0(lVar10);
  }
  pAVar1 = (ApplicationManager *)**(undefined8 **)(lVar10 + 0x28);
  puVar5 = OnToFragmentOver(this,delay);
  if (pAVar1 == (ApplicationManager *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  ApplicationManager::StartCoroutine(pAVar1,puVar5,1);
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
    lVar10 = *plVar7;
    uVar11 = 0;
    if (*(ushort *)(lVar10 + 0x12e) != 0) {
      do {
        if (*(longlong *)(*(longlong *)(lVar10 + 0x70) + (ulonglong)uVar11 * 0x10) ==
            _DAT_1899de560) {
          puVar8 = (undefined8 *)
                   (lVar10 + 0x148 +
                   (ulonglong)
                   (*(int *)(*(longlong *)(lVar10 + 0x70) + 8 + (ulonglong)uVar11 * 0x10) + 1) *
                   0x10);
          goto LAB_1814a13e4;
        }
        uVar11 = uVar11 + 1;
      } while (uVar11 < *(ushort *)(lVar10 + 0x12e));
    }
    puVar8 = (undefined8 *)FUN_1804363c0(plVar7,_DAT_1899de560,1);
LAB_1814a13e4:
    plVar9 = (longlong *)(*(code *)*puVar8)(plVar7,puVar8[1]);
    plVar12 = (longlong *)0x0;
    if (plVar9 != (longlong *)0x0) {
      if ((*(byte *)(*plVar9 + 0x132) < *(byte *)(_DAT_1899e5460 + 0x132)) ||
         (bVar2 = true,
         *(longlong *)
          (*(longlong *)(*plVar9 + 0x50) +
          (longlong)(int)(*(byte *)(_DAT_1899e5460 + 0x132) - 1) * 8) != _DAT_1899e5460)) {
        bVar2 = false;
      }
      if (bVar2) {
        plVar12 = plVar9;
      }
      if (plVar12 == (longlong *)0x0) {
        FUN_1804fe070(plVar9);
        break;
      }
    }
    ExtensionMethods::SetLocalScaleX(plVar12,value);
    ExtensionMethods::SetLocalScaleY(plVar12,value);
    if (plVar12 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    this_00 = (CanvasGroup *)FUN_183978ec0(plVar12,_DAT_189a953f0);
    if (this_00 == (CanvasGroup *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    UnityEngine::CanvasGroup::set_alpha(this_00,value);
  }
  auStack_98[0] = 0x111;
  lVar10 = thunk_FUN_180442320(plVar7,_DAT_1899de570);
  if (lVar10 != 0) {
    FUN_180257630(0,_DAT_1899de570,lVar10);
  }
  PlayVFXSequence(this);
  lVar10 = *_DAT_189a981a8;
  if (*(char *)(lVar10 + 0x136) == '\0') {
    FUN_18043e4c0(lVar10);
  }
  lVar10 = **(longlong **)(lVar10 + 0x90);
  if (*(char *)(lVar10 + 0x136) == '\0') {
    FUN_18043e4c0(lVar10);
  }
  if ((NetworkManager *)**(undefined8 **)(lVar10 + 0x28) == (NetworkManager *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  NetworkManager::RequestHasGotItemIdList((NetworkManager *)**(undefined8 **)(lVar10 + 0x28));
}
else {
  this_01 = IFix::WrappersManagerImpl::GetPatch(0x19a8c);
  if (this_01 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::ILFixDynamicMethodWrapper::Gen_Wrap_13(this_01,(undefined *)this);
}
return;\