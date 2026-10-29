// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 443209

/* ================= 0x1815CF320 ================= */
/* name   = DEALPIKAOFF */
/* entry  = 1815cf320 */
/* body   = 291 bytes */
/* sig    = byte DEALPIKAOFF(Bounds * GAEJLHPNMEB, Bounds * GEEOBLCDDCP) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: bool PHBECOIBOFM::DEALPIKAOFF(UnityEngine.Bounds GAEJLHPNMEB, UnityEngine.Bounds GEEOBLCDDCP)
   [static]  token=06014CCC */

byte MoleMole::PHBECOIBOFM::DEALPIKAOFF(Bounds *GAEJLHPNMEB,Bounds *GEEOBLCDDCP)

{
  code *pcVar1;
  byte bVar2;
  Vector3 *pVVar3;
  ILFixDynamicMethodWrapper *this;
  undefined *P0;
  undefined *P1;
  Vector3 VStack_58;
  Bounds BStack_48;
  float fStack_30;
  float fStack_2c;
  undefined8 uStack_28;
  float fStack_20;
  float fStack_1c;
  float fStack_18;
  float fStack_14;
  undefined8 uStack_10;
  
  bVar2 = IFix::WrappersManagerImpl::IsPatched(0x12363);
  if (bVar2 != 0) {
    this = IFix::WrappersManagerImpl::GetPatch(0x12363);
    BStack_48.m_Extents.y = (GAEJLHPNMEB->m_Center).x;
    BStack_48.m_Extents.z = (GAEJLHPNMEB->m_Center).y;
    fStack_30 = (GAEJLHPNMEB->m_Center).z;
    fStack_2c = (GAEJLHPNMEB->m_Extents).x;
    uStack_28._0_4_ = (GAEJLHPNMEB->m_Extents).y;
    uStack_28._4_4_ = (GAEJLHPNMEB->m_Extents).z;
    P0 = (undefined *)thunk_FUN_18042cf20(_DAT_1899e2b40,&BStack_48.m_Extents.y);
    fStack_20 = (GEEOBLCDDCP->m_Center).x;
    fStack_1c = (GEEOBLCDDCP->m_Center).y;
    fStack_18 = (GEEOBLCDDCP->m_Center).z;
    fStack_14 = (GEEOBLCDDCP->m_Extents).x;
    uStack_10._0_4_ = (GEEOBLCDDCP->m_Extents).y;
    uStack_10._4_4_ = (GEEOBLCDDCP->m_Extents).z;
    P1 = (undefined *)thunk_FUN_18042cf20(_DAT_1899e2b40,&fStack_20);
    if (this != (ILFixDynamicMethodWrapper *)0x0) {
      bVar2 = IFix::ILFixDynamicMethodWrapper::Gen_Wrap_105
                        ((ILFixDynamicMethodWrapper_57479 *)this,P0,P1);
      return bVar2;
    }
    FUN_1804fe400();
    pcVar1 = (code *)swi(3);
    bVar2 = (*pcVar1)();
    return bVar2;
  }
  pVVar3 = UnityEngine::Bounds::get_min(&BStack_48);
  VStack_58.x = pVVar3->x;
  VStack_58.y = pVVar3->y;
  VStack_58.z = pVVar3->z;
  bVar2 = UnityEngine::Bounds::Contains(GAEJLHPNMEB,&VStack_58);
  if (bVar2 == 0) {
    return 0;
  }
  pVVar3 = UnityEngine::Bounds::get_max(&BStack_48);
  VStack_58.x = pVVar3->x;
  VStack_58.y = pVVar3->y;
  VStack_58.z = pVVar3->z;
  bVar2 = UnityEngine::Bounds::Contains(GAEJLHPNMEB,&VStack_58);
  return bVar2;
}



/* ================= 0x181917F10 ================= */
/* name   = ContainPoint */
/* entry  = 181917f10 */
/* body   = 534 bytes */
/* sig    = byte ContainPoint(Bounds * bounds, Vector3 * point, float epsilon) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: bool GeometryUtils::ContainPoint(UnityEngine.Bounds bounds, UnityEngine.Vector3 point, float
   epsilon)  [static]  token=0602987F */

byte MoleMole::GeometryUtils::ContainPoint(Bounds *bounds,Vector3 *point,float epsilon)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  float fVar5;
  code *pcVar6;
  byte bVar7;
  Vector3 *pVVar8;
  ILFixDynamicMethodWrapper *this;
  undefined *P0;
  undefined *P1;
  float fStack_78;
  float fStack_74;
  Bounds BStack_68;
  float fStack_50;
  Bounds BStack_48;
  float fStack_30;
  float fStack_2c;
  undefined8 uStack_28;
  
  bVar7 = IFix::WrappersManagerImpl::IsPatched(0x24171);
  if (bVar7 == 0) {
    pVVar8 = UnityEngine::Bounds::get_min(&BStack_68);
    uVar1 = pVVar8->x;
    BStack_68.m_Center.x = point->x;
    BStack_68.m_Center.y = point->y;
    BStack_68.m_Center.z = point->z;
    if ((float)uVar1 - epsilon <= BStack_68.m_Center.x) {
      uVar2 = point->x;
      pVVar8 = UnityEngine::Bounds::get_max(&BStack_48);
      BStack_68.m_Center.x = pVVar8->x;
      BStack_68.m_Center.y = pVVar8->y;
      BStack_68.m_Center.z = pVVar8->z;
      if ((float)uVar2 <= BStack_68.m_Center.x + epsilon) {
        pVVar8 = UnityEngine::Bounds::get_min(&BStack_48);
        BStack_68.m_Center.x = pVVar8->x;
        BStack_68.m_Center.y = pVVar8->y;
        BStack_68.m_Center.z = pVVar8->z;
        uVar3 = point->y;
        if (BStack_68.m_Center.y - epsilon <= (float)uVar3) {
          uVar4 = point->y;
          pVVar8 = UnityEngine::Bounds::get_max(&BStack_48);
          BStack_68.m_Center.x = pVVar8->x;
          BStack_68.m_Center.y = pVVar8->y;
          BStack_68.m_Center.z = pVVar8->z;
          if ((float)uVar4 <= BStack_68.m_Center.y + epsilon) {
            pVVar8 = UnityEngine::Bounds::get_min(&BStack_48);
            BStack_68.m_Center.z = pVVar8->z;
            fVar5 = point->z;
            if (BStack_68.m_Center.z - epsilon <= fVar5) {
              pVVar8 = UnityEngine::Bounds::get_max(&BStack_48);
              return fVar5 <= pVVar8->z + epsilon;
            }
          }
        }
      }
    }
    bVar7 = 0;
  }
  else {
    this = IFix::WrappersManagerImpl::GetPatch(0x24171);
    BStack_48.m_Extents.y = (bounds->m_Center).x;
    BStack_48.m_Extents.z = (bounds->m_Center).y;
    fStack_30 = (bounds->m_Center).z;
    fStack_2c = (bounds->m_Extents).x;
    uStack_28._0_4_ = (bounds->m_Extents).y;
    uStack_28._4_4_ = (bounds->m_Extents).z;
    P0 = (undefined *)thunk_FUN_18042cf20(_DAT_1899e2b40,&BStack_48.m_Extents.y);
    fStack_50 = point->z;
    BStack_68.m_Extents.y = point->x;
    BStack_68.m_Extents.z = point->y;
    P1 = (undefined *)thunk_FUN_18042cf20(_DAT_1899e2ad8,&BStack_68.m_Extents.y);
    if (this == (ILFixDynamicMethodWrapper *)0x0) {
      FUN_1804fe400();
      pcVar6 = (code *)swi(3);
      bVar7 = (*pcVar6)();
      return bVar7;
    }
    bVar7 = IFix::ILFixDynamicMethodWrapper::Gen_Wrap_2347
                      ((ILFixDynamicMethodWrapper_57479 *)this,P0,P1,epsilon);
  }
  return bVar7;
}



