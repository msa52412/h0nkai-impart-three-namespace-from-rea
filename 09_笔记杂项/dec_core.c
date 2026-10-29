// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 0x1803F53C0 ================= */
/* name   = FUN_1803f53c0 */
/* entry  = 1803f53c0 */
/* body   = 56 bytes */
/* sig    = undefined FUN_1803f53c0() */


DWORD FUN_1803f53c0(HANDLE param_1,LPVOID param_2,DWORD param_3,DWORD *param_4)

{
  BOOL BVar1;
  DWORD DVar2;
  DWORD local_res20 [2];
  
  *param_4 = 0;
  local_res20[0] = 0;
  BVar1 = ReadFile(param_1,param_2,param_3,local_res20,(LPOVERLAPPED)0x0);
  if (BVar1 == 0) {
    DVar2 = GetLastError();
    *param_4 = DVar2;
  }
  return local_res20[0];
}



/* ================= 0x18043AB50 ================= */
/* name   = FUN_18043ab50 */
/* entry  = 18043ab50 */
/* body   = 413 bytes */
/* sig    = undefined FUN_18043ab50() */


ulonglong * FUN_18043ab50(uint param_1)

{
  ulonglong *puVar1;
  ulonglong *puVar2;
  longlong lVar3;
  uint uVar4;
  ulonglong uVar5;
  ulonglong uVar6;
  ulonglong *puVar7;
  ulonglong uVar8;
  ulonglong uVar9;
  uint local_res8 [2];
  uint local_res10;
  int local_res14;
  undefined *local_res18;
  undefined8 uVar10;
  longlong local_40;
  longlong local_38;
  
  uVar10 = 0xfffffffffffffffe;
  if (param_1 == 0xffffffff) {
    puVar1 = (ulonglong *)&DAT_187aebda5;
  }
  else {
    local_res18 = &DAT_1899db6b0;
    local_res8[0] = param_1;
    FUN_1803f4990(&DAT_1899db6b0);
    FUN_18041c210(&DAT_1899db5f0,&local_40,local_res8,(longlong)(int)param_1,uVar10);
    if (((local_40 - DAT_1899db600 & 0xffffffffffffffe0U) + DAT_1899db600 == DAT_1899db608) &&
       (local_38 == 0)) {
      uVar9 = (ulonglong)((int)param_1 >> 0x18 & 0xff);
      puVar1 = (ulonglong *)FUN_1804f1480(DAT_1899dbad0,uVar9 + 1);
      local_res14 = FUN_180432d70(DAT_1899dbad0);
      local_res14 = (int)puVar1 - local_res14;
      local_res10 = param_1;
      FUN_18041ef50(&DAT_1899db5f0,&local_40,&local_res10,&local_res10);
      FUN_1803f72c0(&DAT_1899db6b0);
      uVar6 = (longlong)(int)(param_1 & 0xffffff) * -0x394a88e12ffff3a0 + 0x53db1fc7e9ecc644;
      puVar2 = (ulonglong *)
               (((longlong)DAT_188198e50 ^ 0x7483ff7aU) + (longlong)(int)(param_1 & 0xffffff) +
               DAT_1899dbaf8);
      uVar4 = ((int)param_1 >> 0x18 & 0xffU) + 7;
      if (uVar4 >> 3 != 0) {
        uVar8 = (ulonglong)(uVar4 >> 3);
        puVar7 = puVar1;
        do {
          uVar5 = *puVar2;
          puVar2 = puVar2 + 1;
          uVar5 = uVar5 ^ uVar6;
          uVar6 = uVar6 + 0x64c7ce0352814cf6;
          *puVar7 = uVar5;
          puVar7 = puVar7 + 1;
          uVar8 = uVar8 - 1;
        } while (uVar8 != 0);
      }
      *(undefined1 *)(uVar9 + (longlong)puVar1) = 0;
    }
    else {
      uVar4 = *(uint *)(local_38 + 4);
      lVar3 = FUN_180432d70(DAT_1899dbad0);
      puVar1 = (ulonglong *)((ulonglong)uVar4 + lVar3);
      FUN_1803f72c0(&DAT_1899db6b0);
    }
  }
  return puVar1;
}



/* ================= 0x1803F3790 ================= */
/* name   = FUN_1803f3790 */
/* entry  = 1803f3790 */
/* body   = 57 bytes */
/* sig    = undefined FUN_1803f3790() */


undefined8 FUN_1803f3790(HANDLE param_1,DWORD *param_2)

{
  BOOL BVar1;
  DWORD DVar2;
  LARGE_INTEGER local_res10 [3];
  
  *param_2 = 0;
  BVar1 = GetFileSizeEx(param_1,local_res10);
  if (BVar1 == 0) {
    DVar2 = GetLastError();
    *param_2 = DVar2;
    return 0;
  }
  return local_res10[0].QuadPart;
}



/* ================= 0x1804491A0 ================= */
/* name   = FUN_1804491a0 */
/* entry  = 1804491a0 */
/* body   = 382 bytes */
/* sig    = undefined FUN_1804491a0() */


void FUN_1804491a0(undefined8 param_1)

{
  ulonglong uVar1;
  longlong lVar2;
  ulonglong uVar3;
  longlong lVar4;
  ulonglong uVar5;
  undefined8 local_res8 [4];
  
  local_res8[0] = param_1;
  if ((local_res8 < DAT_1899db6c8) && (DAT_1899db6c0 <= local_res8)) {
    lVar4 = (longlong)local_res8 - (longlong)DAT_1899db6c0;
    if ((DAT_1899db6c8 == DAT_1899db6d0) &&
       ((longlong)DAT_1899db6d0 - (longlong)DAT_1899db6c8 >> 3 == 0)) {
      lVar2 = (longlong)DAT_1899db6c8 - (longlong)DAT_1899db6c0 >> 3;
      if (lVar2 == 0x1fffffffffffffff) {
                    /* WARNING: Subroutine does not return */
        FUN_1804fe5b8("vector<T> too long");
      }
      uVar3 = lVar2 + 1;
      uVar1 = (longlong)DAT_1899db6d0 - (longlong)DAT_1899db6c0 >> 3;
      uVar5 = 0;
      if (uVar1 <= 0x1fffffffffffffff - (uVar1 >> 1)) {
        uVar5 = (uVar1 >> 1) + uVar1;
      }
      if (uVar3 <= uVar5) {
        uVar3 = uVar5;
      }
      FUN_18044f4c0(&DAT_1899db6c0,uVar3);
    }
    if (DAT_1899db6c8 != (undefined8 *)0x0) {
      *DAT_1899db6c8 = DAT_1899db6c0[lVar4 >> 3];
    }
  }
  else {
    if ((DAT_1899db6c8 == DAT_1899db6d0) &&
       ((longlong)DAT_1899db6d0 - (longlong)DAT_1899db6c8 >> 3 == 0)) {
      lVar4 = (longlong)DAT_1899db6c8 - (longlong)DAT_1899db6c0 >> 3;
      if (lVar4 == 0x1fffffffffffffff) {
                    /* WARNING: Subroutine does not return */
        FUN_1804fe5b8("vector<T> too long");
      }
      uVar3 = lVar4 + 1;
      uVar1 = (longlong)DAT_1899db6d0 - (longlong)DAT_1899db6c0 >> 3;
      uVar5 = 0;
      if (uVar1 <= 0x1fffffffffffffff - (uVar1 >> 1)) {
        uVar5 = (uVar1 >> 1) + uVar1;
      }
      if (uVar3 <= uVar5) {
        uVar3 = uVar5;
      }
      FUN_18044f4c0(&DAT_1899db6c0,uVar3);
    }
    if (DAT_1899db6c8 != (undefined8 *)0x0) {
      *DAT_1899db6c8 = param_1;
    }
  }
  DAT_1899db6c8 = DAT_1899db6c8 + 1;
  return;
}



/* ================= 0x180440660 ================= */
/* name   = FUN_180440660 */
/* entry  = 180440660 */
/* body   = 910 bytes */
/* sig    = undefined FUN_180440660() */


void FUN_180440660(void)

{
  int iVar1;
  void **ppvVar2;
  void *pvVar3;
  ulonglong uVar4;
  ulonglong uVar5;
  void ***pppvVar6;
  void **ppvVar7;
  uint uVar8;
  void **ppvVar9;
  void **ppvVar10;
  void **ppvVar11;
  int *piVar12;
  void **local_res8;
  void **local_res10;
  void **local_res18;
  void **local_res20;
  undefined8 uVar13;
  char *local_a0;
  undefined1 local_98;
  void *local_90;
  void **local_88;
  void **local_80;
  undefined **local_78;
  undefined8 local_70;
  undefined8 local_68;
  undefined1 local_60 [8];
  longlong local_58;
  
  uVar13 = 0xfffffffffffffffe;
  ppvVar2 = operator_new(0x60);
  ppvVar10 = (void **)0x0;
  ppvVar7 = ppvVar10;
  local_res18 = ppvVar2;
  if (ppvVar2 != (void **)0x0) {
    local_res8 = (void **)0x0;
    local_res20 = ppvVar2;
    FUN_180400470(ppvVar2 + 1,&local_res8);
    ppvVar2[2] = (void *)0x0;
    ppvVar2[3] = (void *)0x0;
    ppvVar2[4] = (void *)0x0;
    pvVar3 = (void *)FUN_180455a80(ppvVar2);
    ppvVar2[5] = pvVar3;
    ppvVar2[6] = local_res8;
    ppvVar2[7] = (void *)0x0;
    ppvVar2[8] = (void *)0x0;
    if ((void **)0x7fffffff < local_res8) {
      local_78 = std::exception::vftable;
      local_70 = 0;
      local_68 = 0;
      local_a0 = "The map exceeds its maximum size.";
      local_98 = 1;
      __std_exception_copy(&local_a0,&local_70);
      local_78 = std::length_error::vftable;
                    /* WARNING: Subroutine does not return */
      FUN_1804ff8e0(&local_78,&DAT_188d08618);
    }
    if (local_res8 != (void **)0x0) {
      uVar5 = (longlong)local_res8 - 1;
      if (((ulonglong)local_res8 & uVar5) != 0) {
        uVar4 = 1;
        do {
          uVar5 = uVar5 | uVar5 >> ((byte)uVar4 & 0x3f);
          uVar4 = uVar4 * 2;
        } while (uVar4 < 0x40);
        local_res8 = (void **)(uVar5 + 1);
      }
      local_res8 = (void **)((ulonglong)local_res8 >> 6);
      local_res10 = (void **)0x1;
      pppvVar6 = &local_res8;
      if (local_res8 < (void **)0x2) {
        pppvVar6 = &local_res10;
      }
      FUN_1804542f0(ppvVar2 + 2,*pppvVar6);
      ppvVar2[5] = ppvVar2[2];
      *(undefined1 *)((longlong)ppvVar2[3] + -6) = 1;
    }
    FUN_180452d30(ppvVar2,DAT_187975b7c);
    ppvVar7 = ppvVar2;
  }
  ppvVar2 = ppvVar10;
  DAT_1899dbae8 = ppvVar7;
  if (DAT_1881396b0 != 0x4903aafe) {
    do {
      local_res20 = (void **)((longlong)ppvVar2 * 8);
      piVar12 = (int *)((longlong)(DAT_188198e04 + -0x1fe83754) + (longlong)local_res20 +
                       DAT_1899dbaf8);
      local_90 = (void *)0x0;
      local_88 = (void **)0x0;
      local_80 = (void **)0x0;
      ppvVar7 = ppvVar10;
      ppvVar9 = ppvVar10;
      if (0 < piVar12[1]) {
        do {
          iVar1 = *(int *)((DAT_188198e6c + -0x3670df73) + DAT_1899dbaf8 +
                          (longlong)(*piVar12 + (int)ppvVar7) * 4);
          ppvVar11 = ppvVar10;
          if (iVar1 != -1) {
            ppvVar11 = *(void ***)(PTR_PTR_1881a3628 + (longlong)iVar1 * 8);
          }
          local_88 = (void **)((longlong)ppvVar9 + 1);
          if ((void **)((ulonglong)local_80 & 0x7fffffffffffffff) < local_88) {
            local_res10 = (void **)0x1;
            local_res18 = (void **)((longlong)local_80 * 2);
            pppvVar6 = &local_res10;
            if ((void **)((longlong)local_80 * 2) != (void **)0x0) {
              pppvVar6 = &local_res18;
            }
            ppvVar9 = *pppvVar6;
            if ((void **)((ulonglong)local_80 & 0x7fffffffffffffff) < ppvVar9) {
              if (((ulonglong)local_80 & 0x8000000000000000) == 0) {
                local_80 = ppvVar9;
                local_90 = _aligned_realloc(local_90,(longlong)ppvVar9 * 8,8);
              }
              else {
                pvVar3 = _aligned_malloc((longlong)ppvVar9 * 8,8);
                FUN_180500230(pvVar3,local_90,(longlong)local_88 * 8);
                local_90 = pvVar3;
                local_80 = ppvVar9;
              }
            }
          }
          *(void ***)((longlong)local_90 + (longlong)local_88 * 8 + -8) = ppvVar11;
          uVar8 = (int)ppvVar7 + 1;
          ppvVar7 = (void **)(ulonglong)uVar8;
          ppvVar9 = local_88;
        } while ((int)uVar8 < piVar12[1]);
      }
      local_res10 = &local_90;
      FUN_180420010(DAT_1899dbae8,local_60,&local_90,&DAT_18819c364,&local_res10,&local_res8,uVar13)
      ;
      *(undefined8 *)(local_58 + 0x18) = *(undefined8 *)(PTR_PTR_1881396c8 + (longlong)local_res20);
      if (((ulonglong)local_80 & 0x8000000000000000) == 0) {
        thunk_FUN_18050a3d4(local_90);
      }
      uVar8 = (int)ppvVar2 + 1;
      ppvVar2 = (void **)(ulonglong)uVar8;
    } while (uVar8 < DAT_1881396b0 + 0xb6fc5502U);
  }
  return;
}



/* ================= 0x1804F1140 ================= */
/* name   = FUN_1804f1140 */
/* entry  = 1804f1140 */
/* body   = 618 bytes */
/* sig    = undefined FUN_1804f1140() */


undefined8 * FUN_1804f1140(undefined8 *param_1)

{
  ulonglong uVar1;
  undefined8 uVar2;
  undefined8 *puVar3;
  ulonglong uVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  undefined *local_68;
  undefined8 local_60;
  byte local_48;
  undefined7 uStack_47;
  undefined8 local_38;
  ulonglong local_30;
  ulonglong local_28 [2];
  longlong local_18;
  ulonglong local_10;
  
  uVar6 = 0xfffffffffffffffe;
  uVar5 = 0;
  if (DAT_1899de308 == 0) {
    FUN_1803f2970(local_28);
    if (local_18 == 0) {
      if ((DAT_1899de350 == 0) && (0 < DAT_1899de368)) {
        FUN_1804f32f0(&local_48,DAT_1899de328);
        uVar2 = FUN_1803ee7a0(&local_68,&local_48);
        FUN_1803f01c0(&DAT_1899de340,uVar2);
        FUN_1803ed580(&local_68);
        FUN_1803ed580(&local_48);
      }
      param_1[3] = 0xf;
      param_1[2] = 0;
      puVar3 = param_1;
      if (0xf < (ulonglong)param_1[3]) {
        puVar3 = (undefined8 *)*param_1;
      }
      *(undefined1 *)puVar3 = 0;
      FUN_1803f91b0(param_1,&DAT_1899de340,0,0xffffffffffffffff,uVar5,uVar6);
      if (0xf < local_10) {
        uVar4 = local_28[0];
        if (0xfff < local_10 + 1) {
          if ((local_28[0] & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          uVar4 = *(ulonglong *)(local_28[0] - 8);
          if (local_28[0] <= uVar4) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (local_28[0] - uVar4 < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < local_28[0] - uVar4) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(uVar4);
      }
    }
    else {
      uVar6 = FUN_1803ee7a0(&local_48,local_28);
      local_68 = &DAT_1881a61a4;
      local_60 = 4;
      FUN_1803fd190(param_1,uVar6,&local_68);
      if (0xf < local_30) {
        uVar1 = CONCAT71(uStack_47,local_48);
        uVar4 = uVar1;
        if (0xfff < local_30 + 1) {
          if ((local_48 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          uVar4 = *(ulonglong *)(uVar1 - 8);
          if (uVar1 <= uVar4) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (uVar1 - uVar4 < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < uVar1 - uVar4) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(uVar4);
      }
      local_30 = 0xf;
      local_38 = 0;
      local_48 = 0;
      if (0xf < local_10) {
        uVar4 = local_28[0];
        if (0xfff < local_10 + 1) {
          if ((local_28[0] & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          uVar4 = *(ulonglong *)(local_28[0] - 8);
          if (local_28[0] <= uVar4) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (local_28[0] - uVar4 < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < local_28[0] - uVar4) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(uVar4);
      }
    }
  }
  else {
    param_1[3] = 0xf;
    param_1[2] = 0;
    puVar3 = param_1;
    if (0xf < (ulonglong)param_1[3]) {
      puVar3 = (undefined8 *)*param_1;
    }
    *(undefined1 *)puVar3 = 0;
    FUN_1803f91b0(param_1,&DAT_1899de2f8,0,0xffffffffffffffff,0,0xfffffffffffffffe);
  }
  return param_1;
}



/* ================= 0x1803FD190 ================= */
/* name   = FUN_1803fd190 */
/* entry  = 1803fd190 */
/* body   = 60 bytes */
/* sig    = undefined FUN_1803fd190() */


undefined8
FUN_1803fd190(undefined8 param_1,undefined8 *param_2,undefined8 param_3,undefined8 param_4)

{
  undefined8 *local_20;
  undefined8 local_18;
  
  local_18 = param_2[2];
  if (0xf < (ulonglong)param_2[3]) {
    param_2 = (undefined8 *)*param_2;
  }
  local_20 = param_2;
  FUN_1803ee660(param_1,&local_20,param_3,param_4,0);
  return param_1;
}



/* ================= 0x1804F13E0 ================= */
/* name   = FUN_1804f13e0 */
/* entry  = 1804f13e0 */
/* body   = 103 bytes */
/* sig    = undefined FUN_1804f13e0() */


void FUN_1804f13e0(undefined8 *param_1,longlong param_2)

{
  char cVar1;
  
  cVar1 = FUN_1803f0ec0(param_1[1]);
  if (cVar1 != '\0') {
    param_1[1] = param_1[1] + param_2;
    return;
  }
  FUN_1804f34f0("MemoryPool::InternalCommit failed: address 0x%08llx, size %zu, start 0x%08llx, current 0x%08llx, page size 0x%zx"
                ,*param_1,param_2,param_1[1],param_1[2],param_1[3]);
  param_1[1] = 0;
  return;
}



/* ================= 0x1804F1770 ================= */
/* name   = FUN_1804f1770 */
/* entry  = 1804f1770 */
/* body   = 118 bytes */
/* sig    = undefined FUN_1804f1770() */


undefined1 *
FUN_1804f1770(undefined1 *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  longlong lVar1;
  
  lVar1 = FUN_1804f3d50(param_2,0x2e,0xffffffffffffffff,param_4,0);
  if (lVar1 == -1) {
    *(undefined8 *)(param_1 + 0x18) = 0xf;
    *(undefined8 *)(param_1 + 0x10) = 0;
    *param_1 = 0;
    FUN_1803f91b0(param_1,param_2,0,0xffffffffffffffff);
    return param_1;
  }
  FUN_1804561d0(param_2,param_1,0,lVar1);
  return param_1;
}



/* ================= 0x1803F92E0 ================= */
/* name   = FUN_1803f92e0 */
/* entry  = 1803f92e0 */
/* body   = 303 bytes */
/* sig    = undefined FUN_1803f92e0() */


undefined8 * FUN_1803f92e0(undefined8 *param_1,undefined8 *param_2,ulonglong param_3)

{
  ulonglong uVar1;
  undefined8 *puVar2;
  
  if (param_2 != (undefined8 *)0x0) {
    uVar1 = param_1[3];
    puVar2 = param_1;
    if (0xf < uVar1) {
      puVar2 = (undefined8 *)*param_1;
    }
    if (puVar2 <= param_2) {
      puVar2 = param_1;
      if (0xf < uVar1) {
        puVar2 = (undefined8 *)*param_1;
      }
      if (param_2 < (undefined8 *)((longlong)puVar2 + param_1[2])) {
        puVar2 = param_1;
        if (0xf < uVar1) {
          puVar2 = (undefined8 *)*param_1;
        }
        puVar2 = (undefined8 *)
                 FUN_1803f91b0(param_1,param_1,(longlong)param_2 - (longlong)puVar2,param_3);
        return puVar2;
      }
    }
  }
  if (param_3 == 0xffffffffffffffff) {
                    /* WARNING: Subroutine does not return */
    FUN_1804fe5b8("string too long");
  }
  if ((ulonglong)param_1[3] < param_3) {
    FUN_1803f80b0(param_1,param_3,param_1[2]);
    if (param_3 == 0) {
      return param_1;
    }
  }
  else if (param_3 == 0) {
    param_1[2] = 0;
    if (0xf < (ulonglong)param_1[3]) {
      *(undefined1 *)*param_1 = 0;
      return param_1;
    }
    *(undefined1 *)param_1 = 0;
    return param_1;
  }
  puVar2 = param_1;
  if (0xf < (ulonglong)param_1[3]) {
    puVar2 = (undefined8 *)*param_1;
  }
  if (param_3 != 0) {
    FUN_180500230(puVar2,param_2,param_3);
  }
  param_1[2] = param_3;
  puVar2 = param_1;
  if (0xf < (ulonglong)param_1[3]) {
    puVar2 = (undefined8 *)*param_1;
  }
  *(undefined1 *)((longlong)puVar2 + param_3) = 0;
  return param_1;
}



/* ================= 0x180415AC0 ================= */
/* name   = FUN_180415ac0 */
/* entry  = 180415ac0 */
/* body   = 232 bytes */
/* sig    = undefined FUN_180415ac0() */


/* WARNING: Removing unreachable block (ram,0x000180415b84) */

ulonglong FUN_180415ac0(ulonglong param_1)

{
  longlong lVar1;
  ulonglong uVar2;
  
  if ((*(int *)(*(longlong *)((longlong)ThreadLocalStoragePointer + (ulonglong)_tls_index * 8) + 4)
       < DAT_1899db18c) && (_Init_thread_header(&DAT_1899db18c), DAT_1899db18c == -1)) {
    lVar1 = cpuid_Version_info(1);
    DAT_1899db188 = (byte)(*(uint *)(lVar1 + 0xc) >> 0x17) & 1;
    _Init_thread_footer(&DAT_1899db18c,*(undefined4 *)(lVar1 + 8));
  }
  if (DAT_1899db188 == 0) {
    param_1 = param_1 - (param_1 >> 1 & 0x5555555555555555);
    uVar2 = (param_1 >> 2 & 0x3333333333333333) + (param_1 & 0x3333333333333333);
    return ((uVar2 >> 4) + uVar2 & 0xf0f0f0f0f0f0f0f) * 0x101010101010101 >> 0x38;
  }
  return POPCOUNT(param_1);
}



/* ================= 0x180500080 ================= */
/* name   = FUN_180500080 */
/* entry  = 180500080 */
/* body   = 321 bytes */
/* sig    = undefined FUN_180500080() */


undefined1 (*) [16] FUN_180500080(undefined1 (*param_1) [16],byte param_2,ulonglong param_3)

{
  undefined1 (*pauVar1) [16];
  undefined1 (*pauVar2) [16];
  undefined1 uVar3;
  ulonglong uVar6;
  undefined1 auVar7 [16];
  undefined2 uVar4;
  undefined4 uVar5;
  undefined1 auVar8 [16];
  undefined1 auVar9 [16];
  undefined1 auVar10 [16];
  undefined1 auVar11 [16];
  undefined1 auVar12 [16];
  undefined1 auVar13 [16];
  undefined1 auVar14 [16];
  undefined1 auVar15 [16];
  undefined1 auVar16 [16];
  undefined1 uVar17;
  
  uVar6 = (ulonglong)param_2 * 0x101010101010101;
  uVar3 = (undefined1)uVar6;
  uVar4 = (undefined2)uVar6;
  uVar5 = (undefined4)uVar6;
  switch(param_3) {
  case 0:
    return param_1;
  case 8:
    *(ulonglong *)*param_1 = uVar6;
    return param_1;
  case 9:
    *(ulonglong *)(param_1[-1] + param_3 + 7) = uVar6;
    param_1[-1][param_3 + 0xf] = uVar3;
    return param_1;
  case 10:
    *(ulonglong *)*param_1 = uVar6;
    *(undefined2 *)(*param_1 + 8) = uVar4;
    return param_1;
  case 0xb:
    *(ulonglong *)*param_1 = uVar6;
    *(undefined2 *)(*param_1 + 8) = uVar4;
    (*param_1)[10] = uVar3;
    return param_1;
  case 0xc:
    *(ulonglong *)(param_1[-1] + param_3 + 4) = uVar6;
  case 4:
    *(undefined4 *)(param_1[-1] + param_3 + 0xc) = uVar5;
    return param_1;
  case 0xd:
    *(ulonglong *)(param_1[-1] + param_3 + 3) = uVar6;
  case 5:
    *(undefined4 *)(param_1[-1] + param_3 + 0xb) = uVar5;
    param_1[-1][param_3 + 0xf] = uVar3;
    return param_1;
  case 0xe:
    *(ulonglong *)(param_1[-1] + param_3 + 2) = uVar6;
  case 6:
    *(undefined4 *)(param_1[-1] + param_3 + 10) = uVar5;
  case 2:
    *(undefined2 *)(param_1[-1] + param_3 + 0xe) = uVar4;
    return param_1;
  case 0xf:
    *(ulonglong *)(param_1[-1] + param_3 + 1) = uVar6;
  case 7:
    *(undefined4 *)(param_1[-1] + param_3 + 9) = uVar5;
  case 3:
    *(undefined2 *)(param_1[-1] + param_3 + 0xd) = uVar4;
  case 1:
    param_1[-1][param_3 + 0xf] = uVar3;
    return param_1;
  case 0x10:
    *(ulonglong *)*param_1 = uVar6;
    *(ulonglong *)(*param_1 + 8) = uVar6;
    return param_1;
  }
  uVar17 = (undefined1)(uVar6 >> 0x38);
  auVar16._8_6_ = 0;
  auVar16._0_8_ = uVar6;
  auVar16[0xe] = uVar17;
  auVar16[0xf] = uVar17;
  uVar17 = (undefined1)(uVar6 >> 0x30);
  auVar15._14_2_ = auVar16._14_2_;
  auVar15._8_5_ = 0;
  auVar15._0_8_ = uVar6;
  auVar15[0xd] = uVar17;
  auVar14._13_3_ = auVar15._13_3_;
  auVar14._8_4_ = 0;
  auVar14._0_8_ = uVar6;
  auVar14[0xc] = uVar17;
  uVar17 = (undefined1)(uVar6 >> 0x28);
  auVar13._12_4_ = auVar14._12_4_;
  auVar13._8_3_ = 0;
  auVar13._0_8_ = uVar6;
  auVar13[0xb] = uVar17;
  auVar12._11_5_ = auVar13._11_5_;
  auVar12._8_2_ = 0;
  auVar12._0_8_ = uVar6;
  auVar12[10] = uVar17;
  uVar17 = (undefined1)(uVar6 >> 0x20);
  auVar11._10_6_ = auVar12._10_6_;
  auVar11[8] = 0;
  auVar11._0_8_ = uVar6;
  auVar11[9] = uVar17;
  auVar10._9_7_ = auVar11._9_7_;
  auVar10[8] = uVar17;
  auVar10._0_8_ = uVar6;
  uVar17 = (undefined1)(uVar6 >> 0x18);
  auVar9._8_8_ = auVar10._8_8_;
  auVar9[7] = uVar17;
  auVar9[6] = uVar17;
  uVar17 = (undefined1)(uVar6 >> 0x10);
  auVar9[5] = uVar17;
  auVar9[4] = uVar17;
  auVar9._0_4_ = uVar5;
  uVar17 = (undefined1)(uVar6 >> 8);
  auVar8._4_12_ = auVar9._4_12_;
  auVar8[3] = uVar17;
  auVar8[2] = uVar17;
  auVar8._0_2_ = uVar4;
  auVar7._2_14_ = auVar8._2_14_;
  auVar7[1] = uVar3;
  auVar7[0] = uVar3;
  pauVar2 = param_1;
  if (0x80 < param_3) {
    if ((DAT_189be1700 >> 1 & 1) != 0) {
      for (; param_3 != 0; param_3 = param_3 - 1) {
        (*pauVar2)[0] = param_2;
        pauVar2 = (undefined1 (*) [16])(*pauVar2 + 1);
      }
      return param_1;
    }
    *param_1 = auVar7;
    pauVar1 = (undefined1 (*) [16])((ulonglong)(param_1 + 1) & 0xfffffffffffffff0);
    param_3 = (longlong)param_1 + (param_3 - (longlong)pauVar1);
    uVar6 = param_3 >> 7;
    pauVar2 = pauVar1;
    if (uVar6 != 0) {
      do {
        *pauVar1 = auVar7;
        pauVar1[1] = auVar7;
        pauVar2 = pauVar1 + 8;
        pauVar1[2] = auVar7;
        pauVar1[3] = auVar7;
        uVar6 = uVar6 - 1;
        pauVar1[4] = auVar7;
        pauVar1[5] = auVar7;
        pauVar1[6] = auVar7;
        pauVar1[7] = auVar7;
        pauVar1 = pauVar2;
      } while (uVar6 != 0);
      param_3 = param_3 & 0x7f;
    }
  }
  for (uVar6 = param_3 >> 4; uVar6 != 0; uVar6 = uVar6 - 1) {
    *pauVar2 = auVar7;
    pauVar2 = pauVar2 + 1;
  }
  if ((param_3 & 0xf) != 0) {
    *(undefined1 (*) [16])(pauVar2[-1] + (param_3 & 0xf)) = auVar7;
  }
  return param_1;
}



/* ================= 0x1804F3400 ================= */
/* name   = FUN_1804f3400 */
/* entry  = 1804f3400 */
/* body   = 45 bytes */
/* sig    = undefined FUN_1804f3400() */


undefined8 FUN_1804f3400(undefined8 param_1,longlong param_2)

{
  longlong lVar1;
  
  lVar1 = -1;
  do {
    lVar1 = lVar1 + 1;
  } while (*(char *)(param_2 + lVar1) != '\0');
  FUN_1804f3430();
  return param_1;
}



/* ================= 0x1804F4180 ================= */
/* name   = FUN_1804f4180 */
/* entry  = 1804f4180 */
/* body   = 83 bytes */
/* sig    = undefined FUN_1804f4180() */


void FUN_1804f4180(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  undefined8 uVar1;
  undefined8 *puVar2;
  undefined8 local_res10;
  undefined8 local_res18;
  undefined8 local_res20;
  
  local_res10 = param_2;
  local_res18 = param_3;
  local_res20 = param_4;
  uVar1 = __acrt_iob_func(1);
  puVar2 = (undefined8 *)FUN_1803faa60();
  FID_conflict___stdio_common_vfwprintf(*puVar2,uVar1,param_1,0,&local_res10);
  return;
}



/* ================= 0x1804F34F0 ================= */
/* name   = FUN_1804f34f0 */
/* entry  = 1804f34f0 */
/* body   = 159 bytes */
/* sig    = undefined FUN_1804f34f0() */


/* WARNING: Function: _alloca_probe replaced with injection: alloca_probe */

void FUN_1804f34f0(char *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  ulonglong *puVar1;
  undefined8 local_res10;
  undefined8 local_res18;
  undefined8 local_res20;
  undefined8 local_1418;
  undefined4 local_1410;
  char local_140c [5116];
  
  if (param_1 != (char *)0x0) {
    local_1418 = DAT_1881a6080;
    local_1410 = DAT_1881a6088;
    local_res10 = param_2;
    local_res18 = param_3;
    local_res20 = param_4;
    puVar1 = (ulonglong *)FUN_1803faa60();
    common_vsprintf<__crt_stdio_output::standard_base,char>
              (*puVar1 | 2,local_140c,0x13f4,param_1,(__crt_locale_pointers *)0x0,
               (char *)&local_res10);
    (*(code *)PTR_FUN_18993c860)(&local_1418);
  }
  return;
}



