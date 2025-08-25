#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module xử lý nhận diện thông minh tên công ty
Sử dụng fuzzy matching và normalization để khớp các biến thể tên công ty
"""

import re
import unicodedata
from difflib import SequenceMatcher

class CompanyMatcher:
    def __init__(self):
        # Dictionary mapping các biến thể phổ biến
        self.company_aliases = {
            "hòa phú": ["hoa phu", "hòaphú", "hoà phú", "hoà phu", "hòa phu"],
            "nam việt": ["namviet", "namviệt", "nam viet", "namviet", "nam việt"],
            "heineken": ["henieken", "heneiken", "heiniken", "heniken"],
            "soltec": ["solteck", "soltech", "sol tec"],
            "imeco": ["imeco", "imecos"],
            "đại dũng": ["dai dung", "đại dung", "dai đũng"],
            "an tâm": ["an tam", "antam", "an tâm"],
            "thái bình": ["thai binh", "thaibibinh", "thái bình"],
            "hồng hà": ["hong ha", "hồng ha", "hong hà"],
            "minh phát": ["minh phat", "minhphat", "minh phát"],
        }
        
        # Danh sách tên công ty chuẩn (có thể load từ file config)
        self.standard_companies = list(self.company_aliases.keys())
        
        # Ngưỡng độ tương đồng tối thiểu
        self.similarity_threshold = 0.7
    
    def normalize_text(self, text):
        """
        Chuẩn hóa text: loại bỏ dấu, chuyển thành lowercase, loại bỏ ký tự đặc biệt
        """
        if not text:
            return ""
        
        # Chuyển về lowercase
        text = text.lower().strip()
        
        # Loại bỏ dấu tiếng Việt
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Loại bỏ ký tự đặc biệt, chỉ giữ chữ cái và số
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def calculate_similarity(self, text1, text2):
        """
        Tính độ tương đồng giữa 2 chuỗi text
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def find_in_aliases(self, input_name):
        """
        Tìm trong dictionary aliases trước
        """
        normalized_input = self.normalize_text(input_name)
        
        for standard_name, aliases in self.company_aliases.items():
            # Kiểm tra tên chuẩn
            if normalized_input == self.normalize_text(standard_name):
                return standard_name, 1.0
            
            # Kiểm tra các alias
            for alias in aliases:
                if normalized_input == self.normalize_text(alias):
                    return standard_name, 1.0
                    
            # Kiểm tra độ tương đồng với tên chuẩn
            similarity = self.calculate_similarity(normalized_input, self.normalize_text(standard_name))
            if similarity >= self.similarity_threshold:
                return standard_name, similarity
                
            # Kiểm tra độ tương đồng với aliases
            for alias in aliases:
                similarity = self.calculate_similarity(normalized_input, self.normalize_text(alias))
                if similarity >= self.similarity_threshold:
                    return standard_name, similarity
        
        return None, 0.0
    
    def fuzzy_match(self, input_name, company_list=None):
        """
        Fuzzy matching với danh sách công ty
        """
        if company_list is None:
            company_list = self.standard_companies
            
        normalized_input = self.normalize_text(input_name)
        best_match = None
        best_score = 0.0
        
        for company in company_list:
            normalized_company = self.normalize_text(company)
            similarity = self.calculate_similarity(normalized_input, normalized_company)
            
            if similarity > best_score and similarity >= self.similarity_threshold:
                best_score = similarity
                best_match = company
        
        return best_match, best_score
    
    def match_company(self, input_name, company_list=None):
        """
        Hàm chính để khớp tên công ty
        Thử aliases trước, sau đó fuzzy matching
        """
        if not input_name or not input_name.strip():
            return None, 0.0
        
        # Phase 1: Tìm trong aliases dictionary
        match, score = self.find_in_aliases(input_name)
        if match:
            return match, score
        
        # Phase 2: Fuzzy matching với danh sách công ty
        if company_list:
            match, score = self.fuzzy_match(input_name, company_list)
            if match:
                return match, score
        
        # Nếu không tìm thấy, trả về tên gốc đã chuẩn hóa
        return input_name.title(), 0.0
    
    def add_company_alias(self, standard_name, alias):
        """
        Thêm alias mới cho một công ty
        """
        standard_name_lower = standard_name.lower()
        if standard_name_lower not in self.company_aliases:
            self.company_aliases[standard_name_lower] = []
            self.standard_companies.append(standard_name_lower)
        
        if alias.lower() not in self.company_aliases[standard_name_lower]:
            self.company_aliases[standard_name_lower].append(alias.lower())
    
    def get_all_companies(self):
        """
        Lấy danh sách tất cả công ty chuẩn
        """
        return [name.title() for name in self.standard_companies]
    
    def debug_match(self, input_name):
        """
        Debug function để xem quá trình matching
        """
        print(f"\n=== DEBUG COMPANY MATCHING: '{input_name}' ===")
        normalized = self.normalize_text(input_name)
        print(f"Normalized input: '{normalized}'")
        
        # Test aliases
        print("\n--- Testing Aliases ---")
        for standard_name, aliases in self.company_aliases.items():
            print(f"Standard: {standard_name}")
            std_similarity = self.calculate_similarity(normalized, self.normalize_text(standard_name))
            print(f"  Similarity with standard: {std_similarity:.3f}")
            
            for alias in aliases:
                alias_similarity = self.calculate_similarity(normalized, self.normalize_text(alias))
                print(f"  Alias '{alias}': {alias_similarity:.3f}")
        
        # Final result
        match, score = self.match_company(input_name)
        print(f"\nFINAL RESULT: '{match}' (score: {score:.3f})")
        print("=" * 50)
        
        return match, score


# Test function
def test_company_matcher():
    """
    Hàm test để kiểm tra hoạt động của CompanyMatcher
    """
    matcher = CompanyMatcher()
    
    test_cases = [
        "Hòa Phú", "hòaphú", "HÒA PHÚ", "hoa phu", "hoà phú",
        "SOLTEC", "Soltec", "solteck", "sol tec",
        "heneiken", "heineken", "HEINEKEN", "henieken",
        "Nam Việt", "namviet", "NAMVIỆT", "namviệt",
        "Imeco", "IMECO", "imecos",
        "Đại Dũng", "dai dung", "đại dung",
        "An Tâm", "an tam", "antam"
    ]
    
    print("=== TESTING COMPANY MATCHER ===")
    for test_name in test_cases:
        match, score = matcher.match_company(test_name)
        print(f"'{test_name}' -> '{match}' (score: {score:.3f})")
    
    print("\n=== AVAILABLE COMPANIES ===")
    for company in matcher.get_all_companies():
        print(f"- {company}")


if __name__ == "__main__":
    test_company_matcher() 