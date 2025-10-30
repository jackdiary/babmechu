"""
이미지 처리 관련 유틸리티
"""

import os
from PIL import Image, ImageOps, ImageEnhance
from typing import Tuple, Optional
import logging

class ImageValidator:
    """이미지 유효성 검증 클래스"""
    
    # 지원되는 이미지 형식
    SUPPORTED_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP'}
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
    
    # 파일 크기 제한 (16MB)
    MAX_FILE_SIZE = 16 * 1024 * 1024
    
    # 이미지 크기 제한
    MAX_DIMENSION = 4096
    MIN_DIMENSION = 32
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        파일 확장자 검증
        
        Args:
            filename: 파일명
            
        Returns:
            유효성 여부
        """
        if not filename:
            return False
        
        ext = os.path.splitext(filename.lower())[1]
        return ext in ImageValidator.SUPPORTED_EXTENSIONS
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """
        파일 크기 검증
        
        Args:
            file_size: 파일 크기 (bytes)
            
        Returns:
            유효성 여부
        """
        return 0 < file_size <= ImageValidator.MAX_FILE_SIZE
    
    @staticmethod
    def validate_image_content(image_file) -> Tuple[bool, Optional[str]]:
        """
        이미지 내용 검증
        
        Args:
            image_file: 이미지 파일 객체
            
        Returns:
            (유효성 여부, 오류 메시지)
        """
        try:
            # 파일 포인터를 처음으로 이동
            image_file.seek(0)
            
            # PIL로 이미지 열기 시도
            with Image.open(image_file) as img:
                # 이미지 형식 확인
                if img.format not in ImageValidator.SUPPORTED_FORMATS:
                    return False, f"지원되지 않는 이미지 형식입니다: {img.format}"
                
                # 이미지 크기 확인
                width, height = img.size
                
                if width < ImageValidator.MIN_DIMENSION or height < ImageValidator.MIN_DIMENSION:
                    return False, f"이미지가 너무 작습니다. 최소 {ImageValidator.MIN_DIMENSION}x{ImageValidator.MIN_DIMENSION} 픽셀이 필요합니다."
                
                if width > ImageValidator.MAX_DIMENSION or height > ImageValidator.MAX_DIMENSION:
                    return False, f"이미지가 너무 큽니다. 최대 {ImageValidator.MAX_DIMENSION}x{ImageValidator.MAX_DIMENSION} 픽셀까지 지원됩니다."
                
                # 이미지 모드 확인 (RGB로 변환 가능한지)
                if img.mode not in ['RGB', 'RGBA', 'L', 'P']:
                    return False, "지원되지 않는 이미지 모드입니다."
            
            # 파일 포인터를 다시 처음으로 이동
            image_file.seek(0)
            return True, None
            
        except Exception as e:
            logging.error(f"이미지 검증 중 오류: {str(e)}")
            return False, "유효하지 않은 이미지 파일입니다."
    
    @staticmethod
    def get_image_info(image_file) -> Optional[dict]:
        """
        이미지 정보 추출
        
        Args:
            image_file: 이미지 파일 객체
            
        Returns:
            이미지 정보 딕셔너리 또는 None
        """
        try:
            image_file.seek(0)
            
            with Image.open(image_file) as img:
                info = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.size[0],
                    'height': img.size[1]
                }
                
                # EXIF 정보가 있다면 추가
                if hasattr(img, '_getexif') and img._getexif():
                    info['has_exif'] = True
                else:
                    info['has_exif'] = False
                
                return info
                
        except Exception as e:
            logging.error(f"이미지 정보 추출 중 오류: {str(e)}")
            return None
        finally:
            image_file.seek(0)

class ImagePreprocessor:
    """이미지 전처리 클래스"""
    
    @staticmethod
    def resize_and_crop(image: Image.Image, target_size: Tuple[int, int] = (224, 224)) -> Image.Image:
        """
        이미지를 목표 크기로 리사이즈하고 중앙 크롭
        
        Args:
            image: PIL Image 객체
            target_size: 목표 크기 (width, height)
            
        Returns:
            처리된 PIL Image 객체
        """
        # ImageOps.fit을 사용하여 비율을 유지하면서 크롭
        return ImageOps.fit(image, target_size, Image.Resampling.LANCZOS)
    
    @staticmethod
    def normalize_for_model(image: Image.Image) -> Image.Image:
        """
        모델 입력을 위한 이미지 정규화
        
        Args:
            image: PIL Image 객체
            
        Returns:
            정규화된 PIL Image 객체
        """
        # RGB 모드로 변환
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    @staticmethod
    def enhance_image_quality(image: Image.Image) -> Image.Image:
        """
        이미지 품질 개선 (선택적)
        
        Args:
            image: PIL Image 객체
            
        Returns:
            품질이 개선된 PIL Image 객체
        """
        
        # 약간의 선명도 향상
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        # 약간의 대비 향상
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.05)
        
        return image

def get_image_upload_guidelines() -> dict:
    """
    이미지 업로드 가이드라인 반환
    
    Returns:
        가이드라인 딕셔너리
    """
    return {
        'supported_formats': list(ImageValidator.SUPPORTED_FORMATS),
        'max_file_size_mb': ImageValidator.MAX_FILE_SIZE // (1024 * 1024),
        'max_dimension': ImageValidator.MAX_DIMENSION,
        'min_dimension': ImageValidator.MIN_DIMENSION,
        'recommendations': [
            '음식이 화면 중앙에 위치하도록 촬영해주세요',
            '충분한 조명 아래에서 촬영해주세요',
            '음식이 선명하게 보이도록 초점을 맞춰주세요',
            '배경은 단순할수록 좋습니다',
            '음식 전체가 프레임 안에 들어오도록 촬영해주세요'
        ]
    }