-- SQL: add_blockly_xml_to_algorithm.sql
-- Adds blockly_xml column to the algorithm table

-- Add blockly_xml column to algorithm table
ALTER TABLE algorithm 
ADD COLUMN IF NOT EXISTS blockly_xml TEXT;

-- Add comment to the column
COMMENT ON COLUMN algorithm.blockly_xml IS 'Blockly XML データ';
