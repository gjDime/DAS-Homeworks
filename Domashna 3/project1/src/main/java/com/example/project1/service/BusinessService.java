package com.example.project1.service;

import com.example.project1.model.BusinessEntity;
import com.example.project1.model.PriceLogEntity;
import com.example.project1.repository.PriceLogRepository;
import com.example.project1.repository.BusinessRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
@RequiredArgsConstructor
public class BusinessService {

    private final BusinessRepository businessRepository;
    private final PriceLogRepository priceLogRepository;

    public List<BusinessEntity> findAll() {
        return businessRepository.findAll();
    }

    public BusinessEntity findById(Long id) throws Exception {
        return businessRepository.findById(id).orElseThrow(Exception::new);
    }

    public List<PriceLogEntity> findAllToday() {
        return priceLogRepository.findAllByDate(LocalDate.now());
    }

    public List<PriceLogEntity> findAllForCompany(Long id) {
        LocalDate from = LocalDate.now().minusYears(2);
        return priceLogRepository.findByCompanyIdAndDateBetween(id, from, LocalDate.now());
    }

}
