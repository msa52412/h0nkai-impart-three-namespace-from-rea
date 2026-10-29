
bool bVar1;
byte bVar2;
DOCKBAEKMAN *pDVar3;
undefined *puVar4;
DropNewItemDialogContext *pDVar5;
ILFixDynamicMethodWrapper *this;

bVar2 = IFix::WrappersManagerImpl::IsPatched(0xeb75);
if (bVar2 != 0) {
  this = IFix::WrappersManagerImpl::GetPatch(0xeb75);
  if (this == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pDVar5 = IFix::ILFixDynamicMethodWrapper::Gen_Wrap_7103
                     ((ILFixDynamicMethodWrapper_57479 *)this,(undefined *)itemData,useTimer,
                      onlyShow,(undefined *)callback);
  return pDVar5;
}
if (itemData != (StorageDataItemBase *)0x0) {
  puVar4 = itemData->__klass;
  if (((byte)puVar4[0x132] < *(byte *)(_DAT_189a15818 + 0x132)) ||
     (bVar1 = true,
     *(longlong *)
      (*(longlong *)(puVar4 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a15818 + 0x132) - 1) * 8)
     != _DAT_189a15818)) {
    bVar1 = false;
  }
  pDVar3 = (DOCKBAEKMAN *)0x0;
  if (bVar1) {
    pDVar3 = (DOCKBAEKMAN *)itemData;
  }
  if (pDVar3 == (DOCKBAEKMAN *)0x0) {
    if (((byte)puVar4[0x132] < *(byte *)(_DAT_189a17428 + 0x132)) ||
       (bVar1 = true,
       *(longlong *)
        (*(longlong *)(puVar4 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a17428 + 0x132) - 1) * 8
        ) != _DAT_189a17428)) {
      bVar1 = false;
    }
    pDVar3 = (DOCKBAEKMAN *)0x0;
    if (bVar1) {
      pDVar3 = (DOCKBAEKMAN *)itemData;
    }
    if (pDVar3 != (DOCKBAEKMAN *)0x0) {
      puVar4 = DOCKBAEKMAN::KHLBGJJPKOL(pDVar3);
      bVar2 = System::String::IsNullOrEmpty(puVar4);
      if (bVar2 != 0) {
        return (DropNewItemDialogContext *)0x0;
      }
      useTimer = 0;
    }
    pDVar5 = (DropNewItemDialogContext *)il2cpp::codegen::object_new(_DAT_189a1ad38);
    _ctor(pDVar5,itemData,useTimer,onlyShow,callback);
    return pDVar5;
  }
}
return (DropNewItemDialogContext *)0x0;\