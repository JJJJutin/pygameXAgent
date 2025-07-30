"""
增強版 Wall Kick 實現
可以集成到主遊戲中
"""

from config.shapes import WALL_KICK_DATA

def try_wall_kick_enhanced(self, old_rotation, new_rotation):
    """
    增強版踢牆操作（標準SRS + 額外kick序列）
    在標準SRS基礎上添加額外的kick嘗試，提高成功率
    """
    # 首先嘗試標準SRS wall kick
    if self.try_wall_kick_standard(old_rotation, new_rotation):
        return True
    
    # 如果標準kick失敗，嘗試額外的kick序列
    return self.try_additional_kicks(old_rotation, new_rotation)

def try_wall_kick_standard(self, old_rotation, new_rotation):
    """標準SRS Wall Kick實現"""
    # 根據方塊類型選擇對應的 Wall Kick 資料
    if self.current_tetromino.shape_type == "I":
        kick_data_type = "I"
    elif self.current_tetromino.shape_type in ["J", "L", "S", "T", "Z"]:
        kick_data_type = "JLSTZ"
    else:  # O 方塊不需要 Wall Kick
        return False

    # 獲取對應的踢牆測試序列
    kick_tests = WALL_KICK_DATA[kick_data_type].get(
        (old_rotation, new_rotation), []
    )

    # 嘗試每個踢牆位置
    for kick_index, (kick_x, kick_y) in enumerate(kick_tests):
        test_x = self.current_tetromino.x + kick_x
        test_y = self.current_tetromino.y + kick_y

        # 檢查這個位置是否有效
        if self.grid.is_valid_position_at(
            self.current_tetromino.get_rotated_shape(new_rotation), test_x, test_y
        ):
            # 移動到有效位置
            self.current_tetromino.x = test_x
            self.current_tetromino.y = test_y
            self.current_tetromino.rotation = new_rotation

            # 記錄使用的kick類型（用於T-Spin判斷）
            if self.current_tetromino.shape_type == "T":
                self.last_kick_index = kick_index
                self.last_kick_offset = (kick_x, kick_y)

            return True

    return False

def try_additional_kicks(self, old_rotation, new_rotation):
    """嘗試額外的kick序列（針對極端情況）"""
    if self.current_tetromino.shape_type != "T":
        return False  # 目前只為T方塊添加額外kick
    
    # 定義額外的kick序列
    extra_kicks = self.get_extra_kick_sequence(old_rotation, new_rotation)
    
    rotated_shape = self.current_tetromino.get_rotated_shape(new_rotation)
    
    for kick_index, (kick_x, kick_y) in enumerate(extra_kicks):
        test_x = self.current_tetromino.x + kick_x
        test_y = self.current_tetromino.y + kick_y
        
        if self.grid.is_valid_position_at(rotated_shape, test_x, test_y):
            # 移動到有效位置
            self.current_tetromino.x = test_x
            self.current_tetromino.y = test_y
            self.current_tetromino.rotation = new_rotation
            
            # 記錄額外kick信息
            self.last_kick_index = 10 + kick_index  # 區別於標準kick
            self.last_kick_offset = (kick_x, kick_y)
            
            return True
    
    return False

def get_extra_kick_sequence(self, old_rotation, new_rotation):
    """獲取額外的kick序列"""
    extra_kick_data = {
        (0, 1): [(1, 0), (2, 0), (0, 1), (1, 1), (-2, 0), (1, -1)],  # 上->右
        (1, 2): [(0, -1), (1, -1), (-1, 0), (0, -2), (-1, -1)],      # 右->下
        (2, 3): [(-1, 0), (-2, 0), (0, -1), (-1, -1), (2, 0)],       # 下->左
        (3, 0): [(0, 1), (-1, 1), (1, 0), (0, 2), (1, 1)],           # 左->上
        
        # 逆時鐘旋轉的額外kick
        (0, 3): [(-1, 0), (-2, 0), (0, 1), (-1, 1), (2, 0)],         # 上->左
        (3, 2): [(0, -1), (-1, -1), (1, 0), (0, -2), (1, -1)],       # 左->下
        (2, 1): [(1, 0), (2, 0), (0, -1), (1, -1), (-2, 0)],         # 下->右
        (1, 0): [(0, 1), (1, 1), (-1, 0), (0, 2), (-1, 1)],          # 右->上
    }
    
    return extra_kick_data.get((old_rotation, new_rotation), [])