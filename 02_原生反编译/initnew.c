
longlong *plVar1;
bool bVar2;
byte bVar3;
char cVar4;
longlong lVar5;
longlong *plVar6;
undefined8 uVar7;
longlong lVar8;
AvatarCardDataItem *this_00;
longlong lVar9;
undefined8 uVar10;
CFINMGJAHEA *this_01;
AvatarFragmentDataItem *this_02;
MaterialDataItem *this_03;
StorageModule *pSVar11;
StorageDataItemBase *pSVar12;
DropNewItemDialogContext *PCEIPOJCKBI;
ILFixDynamicMethodWrapper *pIVar13;
Call *pCVar14;
undefined *puVar15;
uint uVar16;
longlong lVar17;
Call CStack_58;

CStack_58.currentTop = (undefined *)0x1814a0603;
bVar3 = IFix::WrappersManagerImpl::IsPatched(0x19a86);
if (bVar3 != 0) {
  CStack_58.currentTop = (undefined *)0x1814a0b1a;
  pIVar13 = IFix::WrappersManagerImpl::GetPatch(0x19a86);
  if (pIVar13 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.currentTop = (undefined *)0x1814a0c05;
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
  if (pIVar13->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar13->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar13->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar13->virtualMachine,pIVar13->methodId,&CStack_58,
             (pIVar13->anonObj != (undefined *)0x0) + 1,0);
  return;
}
CStack_58.currentTop = (undefined *)0x1814a0630;
lVar5 = il2cpp::codegen::object_new(_DAT_1899de540);
CStack_58.currentTop = (undefined *)0x1814a063d;
FUN_184a86770(lVar5);
puVar15 = this->itemList;
uVar16 = 0;
if (puVar15 != (undefined *)0x0) {
  lVar17 = 0x20;
  do {
    if (*(int *)(puVar15 + 0x18) <= (int)uVar16) {
      return;
    }
    lVar9 = *_DAT_189a98b00;
    if (*(char *)(lVar9 + 0x136) == '\0') {
      CStack_58.currentTop = (undefined *)0x1814a0679;
      FUN_18043e4c0(lVar9);
    }
    lVar9 = **(longlong **)(lVar9 + 0x90);
    if (*(char *)(lVar9 + 0x136) == '\0') {
      CStack_58.currentTop = (undefined *)0x1814a0694;
      FUN_18043e4c0(lVar9);
    }
    puVar15 = this->itemList;
    pSVar11 = (StorageModule *)**(undefined8 **)(lVar9 + 0x28);
    if (puVar15 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x1814a0bff;
      il2cpp::codegen::raise_null_reference_exception();
    }
    if (*(uint *)(puVar15 + 0x18) <= uVar16) {
      CStack_58.currentTop = (undefined *)0x1814a06b5;
      System::ThrowHelper::ThrowArgumentOutOfRangeException();
    }
    if (*(longlong *)(lVar17 + *(longlong *)(puVar15 + 0x10)) == 0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x1814a0bf9;
      il2cpp::codegen::raise_null_reference_exception();
    }
    if (pSVar11 == (StorageModule *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x1814a0bf3;
      il2cpp::codegen::raise_null_reference_exception();
    }
    CStack_58.currentTop = (undefined *)0x1814a06da;
    bVar3 = StorageModule::IsItemNew
                      (pSVar11,*(int *)(*(longlong *)(lVar17 + *(longlong *)(puVar15 + 0x10)) +
                                       0x14));
    puVar15 = this->itemList;
    if (puVar15 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x1814a0bed;
      il2cpp::codegen::raise_null_reference_exception();
    }
    if (*(uint *)(puVar15 + 0x18) <= uVar16) {
      CStack_58.currentTop = (undefined *)0x1814a06f7;
      System::ThrowHelper::ThrowArgumentOutOfRangeException();
    }
    plVar1 = *(longlong **)(lVar17 + *(longlong *)(puVar15 + 0x10));
    if (plVar1 != (longlong *)0x0) {
      if ((*(byte *)(*plVar1 + 0x132) < *(byte *)(_DAT_189a15818 + 0x132)) ||
         (*(longlong *)
           (*(longlong *)(*plVar1 + 0x50) +
           (longlong)(int)(*(byte *)(_DAT_189a15818 + 0x132) - 1) * 8) != _DAT_189a15818)) {
        bVar2 = false;
      }
      else {
        bVar2 = true;
      }
      plVar6 = (longlong *)0x0;
      if (bVar2) {
        plVar6 = plVar1;
      }
      if (plVar6 != (longlong *)0x0) {
        if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1814a0b63;
          il2cpp::codegen::raise_null_reference_exception();
        }
        CStack_58.currentTop = (undefined *)0x1814a0769;
        uVar7 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
        lVar9 = _DAT_189a15818;
        CStack_58.currentTop = (undefined *)0x1814a077e;
        lVar8 = func_0x000180257760(uVar7,_DAT_189a15818);
        if (lVar8 == 0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1814a0b5d;
          il2cpp::codegen::raise_null_reference_exception();
        }
        CStack_58.currentTop = (undefined *)0x1814a0792;
        this_00 = (AvatarCardDataItem *)func_0x000180257760(uVar7,lVar9);
        CStack_58.currentTop = (undefined *)0x1814a079a;
        bVar3 = AvatarCardDataItem::IsSplite(this_00);
        bVar3 = bVar3 == 0;
      }
    }
    if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x1814a0be7;
      il2cpp::codegen::raise_null_reference_exception();
    }
    CStack_58.currentTop = (undefined *)0x1814a07be;
    uVar7 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
    CStack_58.currentTop = (undefined *)0x1814a07cd;
    lVar9 = func_0x000180257760(uVar7,_DAT_189a18310);
    if (lVar9 != 0) {
      if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1814a0b6f;
        il2cpp::codegen::raise_null_reference_exception();
      }
      CStack_58.currentTop = (undefined *)0x1814a07f0;
      uVar10 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
      uVar7 = _DAT_189a18310;
      CStack_58.currentTop = (undefined *)0x1814a0805;
      lVar9 = func_0x000180257760(uVar10,_DAT_189a18310);
      if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1814a0b69;
        il2cpp::codegen::raise_null_reference_exception();
      }
      CStack_58.currentTop = (undefined *)0x1814a0819;
      this_01 = (CFINMGJAHEA *)func_0x000180257760(uVar10,uVar7);
      CStack_58.currentTop = (undefined *)0x1814a0821;
      bVar3 = CFINMGJAHEA::LJBNHOFKAMN(this_01);
      bVar3 = bVar3 == 0;
    }
    if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x1814a0be1;
      il2cpp::codegen::raise_null_reference_exception();
    }
    CStack_58.currentTop = (undefined *)0x1814a0845;
    uVar7 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
    CStack_58.currentTop = (undefined *)0x1814a0854;
    lVar9 = func_0x000180257760(uVar7,_DAT_189a15a70);
    if (lVar9 != 0) {
      if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1814a0b7b;
        il2cpp::codegen::raise_null_reference_exception();
      }
      CStack_58.currentTop = (undefined *)0x1814a0877;
      uVar10 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
      uVar7 = _DAT_189a15a70;
      CStack_58.currentTop = (undefined *)0x1814a088c;
      lVar9 = func_0x000180257760(uVar10,_DAT_189a15a70);
      if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1814a0b75;
        il2cpp::codegen::raise_null_reference_exception();
      }
      CStack_58.currentTop = (undefined *)0x1814a08a0;
      this_02 = (AvatarFragmentDataItem *)func_0x000180257760(uVar10,uVar7);
      CStack_58.currentTop = (undefined *)0x1814a08a8;
      bVar3 = AvatarFragmentDataItem::IsSplite(this_02);
      bVar3 = bVar3 == 0;
    }
    if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x1814a0bdb;
      il2cpp::codegen::raise_null_reference_exception();
    }
    CStack_58.currentTop = (undefined *)0x1814a08cc;
    uVar7 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
    CStack_58.currentTop = (undefined *)0x1814a08db;
    lVar9 = func_0x000180257760(uVar7,_DAT_189a182e8);
    if (lVar9 != 0) {
      if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1814a0b87;
        il2cpp::codegen::raise_null_reference_exception();
      }
      CStack_58.currentTop = (undefined *)0x1814a08fe;
      uVar10 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
      uVar7 = _DAT_189a182e8;
      CStack_58.currentTop = (undefined *)0x1814a0913;
      lVar9 = func_0x000180257760(uVar10,_DAT_189a182e8);
      if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1814a0b81;
        il2cpp::codegen::raise_null_reference_exception();
      }
      CStack_58.currentTop = (undefined *)0x1814a0927;
      this_03 = (MaterialDataItem *)func_0x000180257760(uVar10,uVar7);
      CStack_58.currentTop = (undefined *)0x1814a092f;
      bVar3 = MaterialDataItem::IsSplite(this_03);
      bVar3 = bVar3 == 0;
    }
    if (bVar3 != 0) {
      if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1814a0bd5;
        il2cpp::codegen::raise_null_reference_exception();
      }
      CStack_58.currentTop = (undefined *)0x1814a095c;
      lVar9 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
      if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1814a0bcf;
        il2cpp::codegen::raise_null_reference_exception();
      }
      if (lVar5 == 0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1814a0bc9;
        il2cpp::codegen::raise_null_reference_exception();
      }
      CStack_58.currentTop = (undefined *)0x1814a097c;
      cVar4 = FUN_184a6d630(lVar5,*(undefined4 *)(lVar9 + 0x14),0);
      if (cVar4 == '\0') {
        CStack_58.currentTop = (undefined *)0x1814a0990;
        pSVar11 = (StorageModule *)FUN_180261460(_DAT_189a98b00);
        if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1814a0bc3;
          il2cpp::codegen::raise_null_reference_exception();
        }
        CStack_58.currentTop = (undefined *)0x1814a09b1;
        pSVar12 = (StorageDataItemBase *)FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
        if (pSVar11 == (StorageModule *)0x0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1814a0bbd;
          il2cpp::codegen::raise_null_reference_exception();
        }
        CStack_58.currentTop = (undefined *)0x1814a09c5;
        bVar3 = StorageModule::IsStorageItemNeedShowShare(pSVar11,pSVar12);
        if (bVar3 == 0) {
          CStack_58.currentTop = (undefined *)0x1814a09d5;
          pSVar11 = (StorageModule *)FUN_180261460(_DAT_189a98b00);
          if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
            CStack_58.currentTop = (undefined *)0x1814a0b99;
            il2cpp::codegen::raise_null_reference_exception();
          }
          CStack_58.currentTop = (undefined *)0x1814a09f6;
          pSVar12 = (StorageDataItemBase *)FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
          if (pSVar11 == (StorageModule *)0x0) {
                  /* WARNING: Subroutine does not return */
            CStack_58.currentTop = (undefined *)0x1814a0b93;
            il2cpp::codegen::raise_null_reference_exception();
          }
          CStack_58.currentTop = (undefined *)0x1814a0a0a;
          bVar3 = StorageModule::IsStorageItemNeedProtectPrompt(pSVar11,pSVar12);
          if (bVar3 == 0) {
            if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
              CStack_58.currentTop = (undefined *)0x1814a0b8d;
              il2cpp::codegen::raise_null_reference_exception();
            }
            CStack_58.currentTop = (undefined *)0x1814a0a2c;
            uVar7 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
            CStack_58.currentTop = (undefined *)0x1814a0a3b;
            lVar9 = func_0x000180257760(uVar7,_DAT_189a17428);
            if (lVar9 == 0) goto LAB_1814a0af6;
          }
        }
        if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1814a0bb7;
          il2cpp::codegen::raise_null_reference_exception();
        }
        CStack_58.currentTop = (undefined *)0x1814a0a62;
        uVar7 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
        CStack_58.currentTop = (undefined *)0x1814a0a71;
        lVar9 = func_0x000180257760(uVar7,_DAT_189a15818);
        if (lVar9 == 0) {
          if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
            CStack_58.currentTop = (undefined *)0x1814a0ba5;
            il2cpp::codegen::raise_null_reference_exception();
          }
          CStack_58.currentTop = (undefined *)0x1814a0a94;
          pSVar12 = (StorageDataItemBase *)FUN_180259080(this->itemList,uVar16);
          CStack_58.currentTop = (undefined *)0x1814a0aa4;
          PCEIPOJCKBI = DropNewItemDialogContext::Create(pSVar12,1,0,(Action *)0x0);
          if (PCEIPOJCKBI != (DropNewItemDialogContext *)0x0) {
            if ((CGGMCLHFCNI *)this->OnDestroyEvent == (CGGMCLHFCNI *)0x0) {
                  /* WARNING: Subroutine does not return */
              CStack_58.currentTop = (undefined *)0x1814a0b9f;
              il2cpp::codegen::raise_null_reference_exception();
            }
            CStack_58.currentTop = (undefined *)0x1814a0ac1;
            CGGMCLHFCNI::DGOHOCLIJID
                      ((CGGMCLHFCNI *)this->OnDestroyEvent,
                       (BaseSequenceDialogContext *)PCEIPOJCKBI);
          }
        }
        if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1814a0bb1;
          il2cpp::codegen::raise_null_reference_exception();
        }
        CStack_58.currentTop = (undefined *)0x1814a0adf;
        lVar9 = FUN_180259080(this->itemList,uVar16,_DAT_189a99060);
        if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1814a0bab;
          il2cpp::codegen::raise_null_reference_exception();
        }
        CStack_58.currentTop = (undefined *)0x1814a0af6;
        FUN_184a6a1f0(lVar5,*(undefined4 *)(lVar9 + 0x14),0);
      }
    }
LAB_1814a0af6:
    puVar15 = this->itemList;
    uVar16 = uVar16 + 1;
    lVar17 = lVar17 + 8;
  } while (puVar15 != (undefined *)0x0);
}
                  /* WARNING: Subroutine does not return */
CStack_58.currentTop = (undefined *)0x1814a0b57;
il2cpp::codegen::raise_null_reference_exception();\