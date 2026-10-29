
byte bVar1;
PointerSpec *this_00;
ILFixDynamicMethodWrapper *pIVar2;
Call *pCVar3;
undefined *puVar4;
Call CStack_68;
undefined8 uStack_40;

uStack_40 = 0x182cc0533;
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x12e1a);
if (bVar1 == 0) {
  uStack_40 = 0x182cc0548;
  this_00 = (PointerSpec *)il2cpp::codegen::object_new(_DAT_189a303d0);
  uStack_40 = 0x182cc0555;
  System::PointerSpec::_ctor(this_00,0);
  if (this_00 != (PointerSpec *)0x0) {
    *(float *)((longlong)&this_00[1].__monitor + 4) = delay;
    this_00[2].__klass = (undefined *)this;
    *(byte *)&this_00[2].__monitor = isRareDrop;
    return (undefined *)this_00;
  }
                  /* WARNING: Subroutine does not return */
  uStack_40 = 0x182cc05b4;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_40 = 0x182cc0589;
pIVar2 = IFix::WrappersManagerImpl::GetPatch(0x12e1a);
if (pIVar2 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_40 = 0x182cc05ba;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_68.argumentBase = (undefined *)0x0;
CStack_68.evaluationStackBase = (undefined *)0x0;
CStack_68.managedStack = (undefined *)0x0;
CStack_68.currentTop = (undefined *)0x0;
CStack_68.topWriteBack = (undefined *)0x0;
pCVar3 = IFix::Core::Call::Begin();
CStack_68.argumentBase = pCVar3->argumentBase;
CStack_68.evaluationStackBase = pCVar3->evaluationStackBase;
CStack_68.managedStack = pCVar3->managedStack;
CStack_68.currentTop = pCVar3->currentTop;
CStack_68.topWriteBack = pCVar3->topWriteBack;
if (pIVar2->anonObj != (undefined *)0x0) {
  IFix::Core::Call::PushObject(&CStack_68,pIVar2->anonObj);
}
IFix::Core::Call::PushObject(&CStack_68,(undefined *)this);
IFix::Core::Call::PushSingle(&CStack_68,delay);
IFix::Core::Call::PushBoolean(&CStack_68,isRareDrop);
if ((VirtualMachine *)pIVar2->virtualMachine != (VirtualMachine *)0x0) {
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar2->virtualMachine,pIVar2->methodId,&CStack_68,
             (pIVar2->anonObj != (undefined *)0x0) + 3,0);
  puVar4 = (undefined *)FUN_18347f130(&CStack_68,0,_DAT_189acb960);
  return puVar4;
}
                  /* WARNING: Subroutine does not return */
il2cpp::codegen::raise_null_reference_exception();\