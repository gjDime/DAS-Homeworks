package com.example.project1.repository;

import com.example.project1.model.BusinessEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface BusinessRepository extends JpaRepository<BusinessEntity, Long> {
    Optional<BusinessEntity> findByCompanyCode(String companyCode);
}
