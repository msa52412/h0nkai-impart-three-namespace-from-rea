byte bVar1;
char cVar2;
undefined8 *puVar3;
ILFixDynamicMethodWrapper *this_00;
undefined *puStack_58;
undefined *puStack_50;
EndlessBaseData *pEStack_48;
puStack_58 = (undefined *)0x0;
puStack_50 = (undefined *)0x0;
pEStack_48 = (EndlessBaseData *)0x0;
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x10820);
if (bVar1 == 0) {
  if (this->baseDataList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */    il2cpp::codegen::raise_null_reference_exception();
  }
  puVar3 = (undefined8 *)FUN_184c6dd10(&stack0xffffffffffffffc0,this->baseDataList,_DAT_189b0e448)  ;
  puStack_58 = (undefined *)*puVar3;
  puStack_50 = (undefined *)puVar3[1];
  pEStack_48 = (EndlessBaseData *)puVar3[2];
  while (cVar2 = FUN_184a5c670(&stack0xffffffffffffffa8), cVar2 != '\0') {
    if (pEStack_48 == (EndlessBaseData *)0x0) {
                  /* WARNING: Subroutine does not return */      il2cpp::codegen::raise_null_reference_exception();
    }
    EndlessBaseData::Refresh(pEStack_48,rsp);
  }
  Mono::Xml::SecurityParser::OnStartParsing            ((SecurityParser *)&stack0xffffffffffffffa8,(SmallXmlParser *)0x0);
  if (rsp == (GetOpenworldEndlessDataRsp *)0x0) {
                  /* WARNING: Subroutine does not return */    il2cpp::codegen::raise_null_reference_exception();
  }
  if (rsp->retcode == 0) {
    if ((OWEndlessWarInfo *)this->WarInfo_k_BackingField == (OWEndlessWarInfo *)0x0) {
                  /* WARNING: Subroutine does not return */      il2cpp::codegen::raise_null_reference_exception();
    }
    OWEndlessWarInfo::Refresh((OWEndlessWarInfo *)this->WarInfo_k_BackingField,rsp);
    RefreshMyScoreByMainRsp(this,rsp);
    RefreshMyItemListByMainRsp(this,rsp);
    RefreshUserLocalData(this,rsp);
    if ((QTInLevelData *)this->qtInLevelData == (QTInLevelData *)0x0) {
                  /* WARNING: Subroutine does not return */      il2cpp::codegen::raise_null_reference_exception();
    }
    QTInLevelData::Refresh((QTInLevelData *)this->qtInLevelData,rsp);
  }
  bVar1 = 0;
}
else {
  this_00 = IFix::WrappersManagerImpl::GetPatch(0x10820);
  if (this_00 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */    il2cpp::codegen::raise_null_reference_exception();
  }
  bVar1 = IFix::ILFixDynamicMethodWrapper::Gen_Wrap_105                    ((ILFixDynamicMethodWrapper_57479 *)this_00,(undefined *)this,(undefined *)rsp                    );
}
return bVar1;
\