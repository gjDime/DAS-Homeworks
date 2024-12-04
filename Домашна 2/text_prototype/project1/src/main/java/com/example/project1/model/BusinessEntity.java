package com.example.project1.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.util.List;

@Entity
@Table(name = "companies")
@Data
@NoArgsConstructor
public class BusinessEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "company_code")
    private String companyCode;

    @Column(name = "last_updated")
    private LocalDate lastUpdated;

    @OneToMany(mappedBy = "company", fetch = FetchType.EAGER)
    private List<PriceLogEntity> historicalData;

    public BusinessEntity(String companyCode) {
        this.companyCode = companyCode;
    }

}
