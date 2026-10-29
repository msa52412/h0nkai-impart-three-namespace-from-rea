// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

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



