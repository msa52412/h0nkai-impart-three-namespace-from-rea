
undefined *puVar1;
RuntimeTypeHandle RVar2;
Type *pTVar3;
ContextPattern *this_00;

puVar1 = (undefined *)il2cpp::codegen::object_new(_DAT_1899e4ea0);
FUN_184ee3ff0(puVar1,0);
if (puVar1 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
FUN_184ebffd0(puVar1,_DAT_18797d4fc,0);
FUN_184ebffd0(puVar1,_DAT_187982c80,0);
FUN_184ebffd0(puVar1,_DAT_187976484,0);
this->DROP_ITEM_PREFAB_PATH = puVar1;
puVar1 = (undefined *)il2cpp::codegen::object_new(_DAT_189a22448);
FUN_184fb8fa0(puVar1,_DAT_189ab27d8);
this->delayTimerSpanList = puVar1;
puVar1 = (undefined *)il2cpp::codegen::object_new(_DAT_1899e8018);
FUN_1851977f0(puVar1,_DAT_189a72b88);
RVar2.value = thunk_FUN_180436090(0x32083);
if (*(int *)(_DAT_1899de380 + 0xe8) == 0) {
  il2cpp::codegen::runtime_class_init();
}
pTVar3 = System::Type::GetTypeFromHandle(RVar2);
if (puVar1 != (undefined *)0x0) {
  FUN_184e58020(puVar1,pTVar3,_DAT_189bbadb0,_DAT_189a72b80);
  RVar2.value = thunk_FUN_180436090(0x316ee);
  pTVar3 = System::Type::GetTypeFromHandle(RVar2);
  FUN_184e58020(puVar1,pTVar3,_DAT_189bbadb8,_DAT_189a72b80);
  RVar2.value = thunk_FUN_180436090(0x32084);
  pTVar3 = System::Type::GetTypeFromHandle(RVar2);
  FUN_184e58020(puVar1,pTVar3,_DAT_189bbadc0,_DAT_189a72b80);
  this->thirdDelayTimer = puVar1;
  ArtifactDetailDialogContext::_ctor((ArtifactDetailDialogContext *)this);
  this_00 = (ContextPattern *)il2cpp::codegen::object_new(_DAT_189a156f8);
  Config::ContextPattern::_ctor(this_00);
  if (this_00 != (ContextPattern *)0x0) {
    this_00->contextName = _DAT_189bbadc8;
    this_00->viewPrefabPath = _DAT_189bbadd0;
    this_00->cacheType = 2;
    this->config = (undefined *)this_00;
    this->dropItemPrefabPathDict = gotItemList;
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
                  /* WARNING: Subroutine does not return */
il2cpp::codegen::raise_null_reference_exception();\