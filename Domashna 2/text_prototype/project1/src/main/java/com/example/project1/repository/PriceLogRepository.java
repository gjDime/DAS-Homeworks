package com.example.project1.repository;

import com.example.project1.model.BusinessEntity;
import com.example.project1.model.PriceLogEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface PriceLogRepository extends JpaRepository<PriceLogEntity, Long> {
    Optional<PriceLogEntity> findByDateAndCompany(LocalDate date, BusinessEntity company);
    List<PriceLogEntity> findByCompanyIdAndDateBetween(Long companyId, LocalDate from, LocalDate to);
    List<PriceLogEntity> findAllByDate(LocalDate date);
}
