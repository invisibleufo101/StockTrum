package com.stocktrum.backend.features.user.repo;

import com.stocktrum.backend.features.user.domain.UserRole;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRoleRepository extends JpaRepository<UserRole, Long> {
  UserRole findByRoleName(String roleName);
}
