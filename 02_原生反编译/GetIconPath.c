
longlong lVar1;
byte bVar2;
char cVar3;
uint uVar4;
undefined8 uVar5;
ILFixDynamicMethodWrapper *pIVar6;
Call *pCVar7;
undefined *puVar8;
KeyNotFoundException *this_00;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x18241f25a;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x16271);
if (bVar2 != 0) {
  uStack_30 = 0x18241f2ef;
  pIVar6 = IFix::WrappersManagerImpl::GetPatch(0x16271);
  if (pIVar6 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18241f31d;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar7 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar7->argumentBase;
  CStack_58.evaluationStackBase = pCVar7->evaluationStackBase;
  CStack_58.managedStack = pCVar7->managedStack;
  CStack_58.currentTop = pCVar7->currentTop;
  CStack_58.topWriteBack = pCVar7->topWriteBack;
  if (pIVar6->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar6->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)storageItem);
  if ((VirtualMachine *)pIVar6->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar6->virtualMachine,pIVar6->methodId,&CStack_58,
               (pIVar6->anonObj != (undefined *)0x0) + 2,0);
    puVar8 = (undefined *)FUN_18347f130(&CStack_58,0,_DAT_189a97140);
    return puVar8;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
if (storageItem == (StorageDataItemBase *)0x0) {
  return (undefined *)**(undefined8 **)(_DAT_1899de428 + 0x28);
}
uStack_30 = 0x18241f26f;
uVar5 = System::Object::GetType((Exception *)storageItem);
if (this->thirdDelayTimer == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x18241f317;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x18241f291;
cVar3 = FUN_184e58140(this->thirdDelayTimer,uVar5,_DAT_189aaa5e0);
if (cVar3 == '\0') {
  return _DAT_189bbadd8;
}
puVar8 = this->thirdDelayTimer;
if (puVar8 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x18241f311;
  il2cpp::codegen::raise_null_reference_exception();
}
if (puVar8 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x184e77619;
  il2cpp::codegen::raise_null_reference_exception(0,uVar5);
}
uStack_30 = 0x184e775b4;
uVar4 = FUN_184e5ac50(puVar8,uVar5,*(undefined8 *)(*(longlong *)(*_DAT_189aaa5e8 + 0x90) + 0x88));
if (-1 < (int)uVar4) {
  lVar1 = *(longlong *)(puVar8 + 0x18);
  if (lVar1 == 0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x184e77613;
    il2cpp::codegen::raise_null_reference_exception();
  }
  if (uVar4 < *(uint *)(lVar1 + 0x18)) {
    return *(undefined **)(lVar1 + 0x30 + (longlong)(int)uVar4 * 0x18);
  }
  uStack_30 = 0x184e77603;
  uVar5 = il2cpp::codegen::get_index_out_of_range_exception();
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x184e7760d;
  il2cpp::codegen::raise_exception(uVar5,0);
}
uStack_30 = 0x184e775e3;
this_00 = (KeyNotFoundException *)il2cpp::codegen::object_new(_DAT_1899e0068);
uStack_30 = 0x184e775ee;
System::Collections::Generic::KeyNotFoundException::_ctor(this_00);
                  /* WARNING: Subroutine does not return */
uStack_30 = 0x184e775fd;
il2cpp::codegen::raise_exception(this_00,_DAT_189b36228);\